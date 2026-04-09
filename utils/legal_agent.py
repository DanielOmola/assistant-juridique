# legal_agent.py
from typing import List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseLLM
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.outputs import LLMResult, Generation
import json
from utils.utils_logging import get_logger

logger = get_logger(__name__)


class LangChainLLMAdapter(BaseLLM):
    """Adaptateur pour utiliser votre llm_client avec LangChain"""
    
    def __init__(self, llm_client, system_prompt: str = "Tu es un expert juridique."):
        super().__init__()
        self.llm_client = llm_client
        self.modele_actif = llm_client.modele_actif if hasattr(llm_client, 'modele_actif') else None
        self.system_prompt = system_prompt
    
    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None, 
                  run_manager: Optional[CallbackManagerForToolRun] = None, **kwargs):
        """Implémente l'interface LangChain"""
        results = []
        
        for prompt in prompts:
            try:
                # Utiliser votre llm_client exactement comme dans votre code
                result = self.llm_client.call_llm(
                    prompt=prompt,
                    system_prompt=self.system_prompt,
                    model=self.modele_actif,
                    temperature=0.3
                )
                
                if result and not result.get("error"):
                    content = result.get("content", "")
                    results.append(content if content else "Aucune réponse générée")
                else:
                    error_msg = result.get("error", "Erreur inconnue") if result else "Résultat vide"
                    logger.error(f"Erreur LLM: {error_msg}")
                    results.append(f"Erreur: {error_msg}")
                    
            except Exception as e:
                logger.error(f"Exception lors de l'appel LLM: {str(e)}")
                results.append(f"Erreur technique: {str(e)}")
        
        # Format requis par LangChain
        generations = [[Generation(text=text)] for text in results]
        return LLMResult(generations=generations)
    
    @property
    def _llm_type(self) -> str:
        return "custom_llm_adapter"
    
    @property
    def _identifying_params(self) -> dict:
        """Required property for BaseLLM"""
        return {"model": self.modele_actif, "system_prompt": self.system_prompt}


class LegalResearchAgent:
    """Agent juridique pour la recherche et l'analyse sur sources officielles"""
    
    def __init__(self, llm_client, prompt: str, system_prompt: str = "Tu es un expert juridique assistant un avocat."):
        """
        Args:
            llm_client: Votre client LLM existant
            prompt: Le prompt à utiliser pour l'agent
            system_prompt: Le system prompt par défaut
        """
        self.llm_client = llm_client
        self.prompt = prompt
        self.system_prompt = system_prompt
        
        # Adapter votre LLM pour LangChain
        self.llm = LangChainLLMAdapter(llm_client, system_prompt)
        
        # Créer les outils
        self.tools = self._create_tools()
        
        # Créer l'agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=False,
            max_iterations=3,
            handle_parsing_errors=True
        )
    
    def _create_tools(self) -> List[Tool]:
        """Crée les outils disponibles pour l'agent"""
        
        def search_legifrance(query: str) -> str:
            """Recherche sur Légifrance"""
            return self._search_legal_source(query, "Légifrance", "https://www.legifrance.gouv.fr")
        
        def search_cour_cassation(query: str) -> str:
            """Recherche sur Cour de Cassation"""
            return self._search_legal_source(query, "Cour de Cassation", "https://www.courdecassation.fr")
        
        def search_conseil_etat(query: str) -> str:
            """Recherche sur Conseil d'État"""
            return self._search_legal_source(query, "Conseil d'État", "https://www.conseil-etat.fr")
        
        def search_eur_lex(query: str) -> str:
            """Recherche sur EUR-Lex"""
            return self._search_legal_source(query, "EUR-Lex", "https://eur-lex.europa.eu")
        
        def search_service_public(query: str) -> str:
            """Recherche sur Service-Public.fr"""
            return self._search_legal_source(query, "Service-Public", "https://www.service-public.fr")
        
        def search_dalloz(query: str) -> str:
            """Recherche sur Dalloz"""
            return self._search_legal_source(query, "Dalloz", "https://www.dalloz.fr")
        
        def search_doctrine(query: str) -> str:
            """Recherche sur Doctrine.fr"""
            return self._search_legal_source(query, "Doctrine", "https://www.doctrine.fr")
        
        def search_justice(query: str) -> str:
            """Recherche sur Justice.fr"""
            return self._search_legal_source(query, "Justice.fr", "https://www.justice.fr")
        
        return [
            Tool(name="recherche_legifrance", func=search_legifrance, 
                 description="Recherche sur Légifrance pour les lois, codes, décrets et jurisprudence"),
            Tool(name="recherche_cour_cassation", func=search_cour_cassation,
                 description="Recherche sur la Cour de Cassation pour la jurisprudence judiciaire"),
            Tool(name="recherche_conseil_etat", func=search_conseil_etat,
                 description="Recherche sur le Conseil d'État pour la jurisprudence administrative"),
            Tool(name="recherche_eur_lex", func=search_eur_lex,
                 description="Recherche sur EUR-Lex pour les traités, règlements et directives européens"),
            Tool(name="recherche_service_public", func=search_service_public,
                 description="Recherche sur Service-Public.fr pour les démarches et droits des citoyens"),
            Tool(name="recherche_dalloz", func=search_dalloz,
                 description="Recherche sur Dalloz pour la doctrine et la jurisprudence commentée"),
            Tool(name="recherche_doctrine", func=search_doctrine,
                 description="Recherche sur Doctrine.fr pour les analyses juridiques"),
            Tool(name="recherche_justice", func=search_justice,
                 description="Recherche sur Justice.fr pour les informations ministérielles"),
        ]
    
    def _search_legal_source(self, query: str, source_name: str, base_url: str) -> str:
        """Recherche sur une source juridique spécifique"""
        try:
            # Prompt pour simuler la recherche sur la source juridique
            search_prompt = f"""
            En tant qu'expert juridique, recherche sur {source_name} ({base_url}) les informations pertinentes concernant: {query}
            
            Quels sont les articles de loi, décisions de justice, ou documents officiels que l'on trouverait sur ce site?
            Fournis des références précises et des extraits pertinents.
            """
            
            result = self.llm_client.call_llm(
                prompt=search_prompt,
                system_prompt=f"Tu es un expert juridique spécialisé dans la recherche sur {source_name}",
                model=self.llm.modele_actif,
                temperature=0.2
            )
            
            if result and not result.get("error"):
                content = result.get('content', '')
                return f"📚 **{source_name}**\n{content}\n"
            else:
                return f"❌ Aucune information trouvée sur {source_name}"
                
        except Exception as e:
            logger.error(f"Erreur recherche {source_name}: {str(e)}")
            return f"⚠️ Erreur lors de la recherche sur {source_name}: {str(e)}"
    
    def _create_agent(self):
        """Crée l'agent React avec le prompt personnalisé"""
        
        react_template = """Tu es un expert juridique. Tu as accès à des outils de recherche sur les sources juridiques officielles françaises et européennes.

{tools}

À utiliser au format suivant:

Question: la question à laquelle tu dois répondre
Thought: réfléchis à ce que tu dois faire
Action: l'action à exécuter (une des {tool_names})
Action Input: l'input pour l'action
Observation: le résultat de l'action
... (répète Thought/Action/Action Input/Observation autant de fois que nécessaire)
Thought: J'ai maintenant la réponse
Final Answer: la réponse finale à l'utilisateur

Commence!

Question: {input}
Thought: {agent_scratchpad}
"""
        
        prompt_template = PromptTemplate.from_template(react_template)
        
        from langchain.agents import create_react_agent
        return create_react_agent(self.llm, self.tools, prompt_template)
    
    def analyze(self, context: str) -> str:
        """
        Analyse le dossier avec l'agent
        
        Args:
            context: Le texte du dossier à analyser
            
        Returns:
            L'analyse complète générée par l'agent
        """
        try:
            # Utiliser le prompt passé au constructeur
            full_prompt = f"{self.prompt}\n\nContexte du dossier:\n{context}"
            
            # Exécuter l'agent
            response = self.agent_executor.invoke({"input": full_prompt})
            return response.get("output", "❌ Aucune analyse générée")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse par l'agent: {str(e)}")
            return f"❌ Erreur de l'agent: {str(e)}"