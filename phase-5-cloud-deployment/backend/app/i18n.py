"""
Internationalization (i18n) System

Multi-language support for the application.
"""

import logging
from typing import Dict, Any, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class Translation:
    """Translation manager."""

    def __init__(self, locale: str = "en"):
        """Initialize translation."""
        self.locale = locale
        self.translations: Dict[str, Dict[str, str]] = {}
        self.fallback_locale = "en"

    def load_translations(self, locale: str, translations: Dict[str, str]):
        """Load translations for locale."""
        self.translations[locale] = translations
        logger.info(f"Loaded {len(translations)} translations for {locale}")

    def load_from_file(self, locale: str, file_path: str):
        """Load translations from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)
                self.load_translations(locale, translations)
        except Exception as e:
            logger.error(f"Error loading translations from {file_path}: {e}")

    def translate(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        """Translate key to locale."""
        locale = locale or self.locale

        # Try requested locale
        if locale in self.translations and key in self.translations[locale]:
            text = self.translations[locale][key]
        # Try fallback locale
        elif self.fallback_locale in self.translations and key in self.translations[self.fallback_locale]:
            text = self.translations[self.fallback_locale][key]
        # Return key if not found
        else:
            logger.warning(f"Translation not found: {key} ({locale})")
            return key

        # Format with kwargs
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                logger.error(f"Missing format parameter: {e}")

        return text

    def t(self, key: str, **kwargs) -> str:
        """Shorthand for translate."""
        return self.translate(key, **kwargs)

    def set_locale(self, locale: str):
        """Set current locale."""
        self.locale = locale

    def get_available_locales(self) -> list[str]:
        """Get available locales."""
        return list(self.translations.keys())


# Global translation instance
i18n = Translation()

# English translations
EN_TRANSLATIONS = {
    "app.name": "Todo App",
    "app.welcome": "Welcome to Todo App",

    # Common
    "common.save": "Save",
    "common.cancel": "Cancel",
    "common.delete": "Delete",
    "common.edit": "Edit",
    "common.create": "Create",
    "common.update": "Update",
    "common.search": "Search",
    "common.filter": "Filter",
    "common.loading": "Loading...",
    "common.error": "Error",
    "common.success": "Success",

    # Todos
    "todo.title": "Title",
    "todo.description": "Description",
    "todo.priority": "Priority",
    "todo.due_date": "Due Date",
    "todo.completed": "Completed",
    "todo.tags": "Tags",
    "todo.create": "Create Todo",
    "todo.update": "Update Todo",
    "todo.delete": "Delete Todo",
    "todo.mark_complete": "Mark as Complete",
    "todo.overdue": "Overdue",

    # Messages
    "message.todo_created": "Todo created successfully",
    "message.todo_updated": "Todo updated successfully",
    "message.todo_deleted": "Todo deleted successfully",
    "message.todo_completed": "Todo marked as complete",

    # Errors
    "error.not_found": "Not found",
    "error.unauthorized": "Unauthorized",
    "error.validation": "Validation error",
    "error.server": "Server error",
    "error.network": "Network error",

    # Validation
    "validation.required": "{field} is required",
    "validation.min_length": "{field} must be at least {min} characters",
    "validation.max_length": "{field} must be at most {max} characters",
    "validation.invalid_email": "Invalid email address",
    "validation.invalid_url": "Invalid URL",
}

# Spanish translations
ES_TRANSLATIONS = {
    "app.name": "Aplicación de Tareas",
    "app.welcome": "Bienvenido a la Aplicación de Tareas",

    # Common
    "common.save": "Guardar",
    "common.cancel": "Cancelar",
    "common.delete": "Eliminar",
    "common.edit": "Editar",
    "common.create": "Crear",
    "common.update": "Actualizar",
    "common.search": "Buscar",
    "common.filter": "Filtrar",
    "common.loading": "Cargando...",
    "common.error": "Error",
    "common.success": "Éxito",

    # Todos
    "todo.title": "Título",
    "todo.description": "Descripción",
    "todo.priority": "Prioridad",
    "todo.due_date": "Fecha de Vencimiento",
    "todo.completed": "Completado",
    "todo.tags": "Etiquetas",
    "todo.create": "Crear Tarea",
    "todo.update": "Actualizar Tarea",
    "todo.delete": "Eliminar Tarea",
    "todo.mark_complete": "Marcar como Completado",
    "todo.overdue": "Vencido",

    # Messages
    "message.todo_created": "Tarea creada exitosamente",
    "message.todo_updated": "Tarea actualizada exitosamente",
    "message.todo_deleted": "Tarea eliminada exitosamente",
    "message.todo_completed": "Tarea marcada como completada",

    # Errors
    "error.not_found": "No encontrado",
    "error.unauthorized": "No autorizado",
    "error.validation": "Error de validación",
    "error.server": "Error del servidor",
    "error.network": "Error de red",

    # Validation
    "validation.required": "{field} es requerido",
    "validation.min_length": "{field} debe tener al menos {min} caracteres",
    "validation.max_length": "{field} debe tener como máximo {max} caracteres",
    "validation.invalid_email": "Dirección de correo electrónico inválida",
    "validation.invalid_url": "URL inválida",
}

# French translations
FR_TRANSLATIONS = {
    "app.name": "Application de Tâches",
    "app.welcome": "Bienvenue dans l'Application de Tâches",

    # Common
    "common.save": "Enregistrer",
    "common.cancel": "Annuler",
    "common.delete": "Supprimer",
    "common.edit": "Modifier",
    "common.create": "Créer",
    "common.update": "Mettre à jour",
    "common.search": "Rechercher",
    "common.filter": "Filtrer",
    "common.loading": "Chargement...",
    "common.error": "Erreur",
    "common.success": "Succès",

    # Todos
    "todo.title": "Titre",
    "todo.description": "Description",
    "todo.priority": "Priorité",
    "todo.due_date": "Date d'échéance",
    "todo.completed": "Terminé",
    "todo.tags": "Étiquettes",
    "todo.create": "Créer une Tâche",
    "todo.update": "Mettre à jour la Tâche",
    "todo.delete": "Supprimer la Tâche",
    "todo.mark_complete": "Marquer comme Terminé",
    "todo.overdue": "En retard",

    # Messages
    "message.todo_created": "Tâche créée avec succès",
    "message.todo_updated": "Tâche mise à jour avec succès",
    "message.todo_deleted": "Tâche supprimée avec succès",
    "message.todo_completed": "Tâche marquée comme terminée",

    # Errors
    "error.not_found": "Non trouvé",
    "error.unauthorized": "Non autorisé",
    "error.validation": "Erreur de validation",
    "error.server": "Erreur du serveur",
    "error.network": "Erreur réseau",

    # Validation
    "validation.required": "{field} est requis",
    "validation.min_length": "{field} doit contenir au moins {min} caractères",
    "validation.max_length": "{field} doit contenir au maximum {max} caractères",
    "validation.invalid_email": "Adresse e-mail invalide",
    "validation.invalid_url": "URL invalide",
}

# Load default translations
i18n.load_translations("en", EN_TRANSLATIONS)
i18n.load_translations("es", ES_TRANSLATIONS)
i18n.load_translations("fr", FR_TRANSLATIONS)


# Helper functions
def translate(key: str, locale: Optional[str] = None, **kwargs) -> str:
    """Translate key."""
    return i18n.translate(key, locale, **kwargs)


def t(key: str, **kwargs) -> str:
    """Shorthand for translate."""
    return i18n.t(key, **kwargs)


def set_locale(locale: str):
    """Set current locale."""
    i18n.set_locale(locale)


def get_locale() -> str:
    """Get current locale."""
    return i18n.locale
