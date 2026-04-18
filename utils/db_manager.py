import sqlite3
import os
import sys
from pathlib import Path

def get_db_path():
    """Database in exe folder with fallback to Documents"""
    if getattr(sys, 'frozen', False):
        # Running as .exe
        exe_dir = os.path.dirname(sys.executable)
        db_path = os.path.join(exe_dir, 'llm_providers.db')
        
        # Test write permission in exe directory
        try:
            test_file = os.path.join(exe_dir, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return db_path
        except:
            # Fallback to Documents
            docs = os.path.join(os.path.expanduser('~'), 'Documents', 'AssistantJuridique')
            os.makedirs(docs, exist_ok=True)
            return os.path.join(docs, 'llm_providers.db')
    else:
        # Running as script
        return Path(__file__).parent.parent / "llm_providers.db"

DB_PATH = get_db_path()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with tables and default data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create providers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS providers (
            name TEXT UNIQUE PRIMARY KEY NOT NULL,
            api_key TEXT,
            url TEXT NOT NULL
        )
    """)
    
    # Create models table with CASCADE delete
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            model_key TEXT UNIQUE PRIMARY KEY NOT NULL,
            provider_name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            context_length INTEGER NOT NULL,
            FOREIGN KEY (provider_name) REFERENCES providers (name) ON DELETE CASCADE
        )
    """)
    
    # Check if default providers exist
    cursor.execute("SELECT COUNT(*) as count FROM providers")
    if cursor.fetchone()['count'] == 0:
        # Insert default providers
        default_providers = [
            ('openai', 'https://api.openai.com/v1'),
            ('anthropic', 'https://api.anthropic.com/v1'),
            ('groq', 'https://api.groq.com/openai/v1'),
            ('google', 'https://generativelanguage.googleapis.com/v1')
        ]
        cursor.executemany(
            "INSERT INTO providers (name, url) VALUES (?, ?)",
            default_providers
        )
        
        # Insert default models
        default_models = [
            ('gpt-5.4', 'openai', 'GPT-5.4 (recommandé)', 1050000),
            ('gpt-5.4-mini', 'openai', 'GPT-5.4 mini', 400000),
            ('gpt-5.4-nano', 'openai', 'GPT-5.4 nano (rapide/peu cher)', 400000),
            ('claude-opus-4-6', 'anthropic', 'Claude Opus 4.6 (meilleur juridique)', 1000000),
            ('claude-sonnet-4-6', 'anthropic', 'Claude Sonnet 4.6 (très précis)', 1000000),
            ('claude-haiku-4-5-20251001', 'anthropic', 'Claude Haiku 4.5 (rapide)', 200000),
            ('llama-3.3-70b-versatile', 'groq', 'Llama 3.3 70B (gratuit/rapide)', 131072),
            ('llama-3.1-8b-instant', 'groq', 'Llama 3.1 8B', 131072),
            ('openai/gpt-oss-120b', 'groq', 'GPT OSS 120B', 131072),
            ('openai/gpt-oss-20b', 'groq', 'GPT OSS 20B', 131072),
            ('gemini-3.1-pro-preview', 'google', 'Gemini 3.1 Pro (preview)', 1048576),
            ('gemini-3-flash-preview', 'google', 'Gemini 3 Flash', 131072),
            ('gemini-3.1-flash-lite-preview', 'google', 'Gemini 3.1 Flash-Lite Preview', 131072)
        ]
        cursor.executemany(
            "INSERT INTO models (model_key, provider_name, display_name, context_length) VALUES (?, ?, ?, ?)",
            default_models
        )
        
        conn.commit()
    
    conn.close()

    
def get_all_providers():
    """Get all providers"""
    conn = get_db_connection()
    providers = conn.execute("SELECT name, url, api_key FROM providers ORDER BY name").fetchall()
    conn.close()
    return [dict(p) for p in providers]

def get_provider(name):
    """Get provider by name"""
    conn = get_db_connection()
    provider = conn.execute("SELECT name, url, api_key FROM providers WHERE name = ?", (name,)).fetchone()
    conn.close()
    return dict(provider) if provider else None

def insert_provider(name, url, api_key=None):
    """Insert a new provider"""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO providers (name, url, api_key) VALUES (?, ?, ?)",
            (name, url, api_key)
        )
        conn.commit()
        return True, f"Provider '{name}' inserted successfully"
    except sqlite3.IntegrityError:
        return False, f"Provider '{name}' already exists"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_provider(name):
    """Delete a provider and all its models"""
    conn = get_db_connection()
    try:
        # Check if exists
        provider = conn.execute("SELECT name FROM providers WHERE name = ?", (name,)).fetchone()
        if not provider:
            return False, f"Provider '{name}' not found"
        
        conn.execute("DELETE FROM providers WHERE name = ?", (name,))
        conn.commit()
        return True, f"Provider '{name}' and all its models deleted successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_provider_api_key(name, api_key):
    """Update provider's API key"""
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE providers SET api_key = ? WHERE name = ?",
            (api_key, name)
        )
        conn.commit()
        if conn.total_changes > 0:
            return True, f"API key updated for provider '{name}'"
        return False, f"Provider '{name}' not found"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_models_by_provider(provider_name):
    """Get all models for a specific provider"""
    conn = get_db_connection()
    models = conn.execute(
        "SELECT model_key, display_name, context_length FROM models WHERE provider_name = ? ORDER BY model_key",
        (provider_name,)
    ).fetchall()
    conn.close()
    return [dict(m) for m in models]

def get_all_models():
    """Get all models with provider info"""
    conn = get_db_connection()
    models = conn.execute("""
        SELECT m.model_key, m.provider_name, m.display_name, m.context_length, p.api_key, p.url
        FROM models m
        JOIN providers p ON m.provider_name = p.name
        ORDER BY m.provider_name, m.model_key
    """).fetchall()
    conn.close()
    return [dict(m) for m in models]

def get_available_models():
    """Get only models whose provider has a non-empty API key"""
    conn = get_db_connection()
    models = conn.execute("""
        SELECT m.model_key, m.provider_name, m.display_name, m.context_length, p.url
        FROM models m
        JOIN providers p ON m.provider_name = p.name
        WHERE p.api_key IS NOT NULL AND p.api_key != ''
        ORDER BY m.provider_name, m.model_key
    """).fetchall()
    conn.close()
    return [dict(m) for m in models]

def insert_model(model_key, provider_name, display_name, context_length):
    """Insert a new model"""
    conn = get_db_connection()
    try:
        # Check if provider exists
        provider = conn.execute("SELECT name FROM providers WHERE name = ?", (provider_name,)).fetchone()
        if not provider:
            return False, f"Provider '{provider_name}' not found"
        
        conn.execute(
            "INSERT INTO models (model_key, provider_name, display_name, context_length) VALUES (?, ?, ?, ?)",
            (model_key, provider_name, display_name, context_length)
        )
        conn.commit()
        return True, f"Model '{model_key}' inserted successfully"
    except sqlite3.IntegrityError:
        return False, f"Model '{model_key}' already exists"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_model(model_key):
    """Delete a specific model"""
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM models WHERE model_key = ?", (model_key,))
        conn.commit()
        if conn.total_changes > 0:
            return True, f"Model '{model_key}' deleted successfully"
        return False, f"Model '{model_key}' not found"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()