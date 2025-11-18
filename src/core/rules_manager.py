"""
Rules Manager - Load, save, and manage evaluation rules
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from src.utils.logger import configured_logger


class RulesManager:
    """Manages loading and saving of evaluation rules"""
    
    def __init__(self, rules_file: str = None):
        """
        Initialize the rules manager.
        
        Args:
            rules_file: Path to the rules JSON file. If None, uses default location.
        """
        if rules_file is None:
            # Default to config/rules.json in project root
            # Path: src/core/rules_manager.py -> src/core -> src -> project_root
            project_root = Path(__file__).resolve().parent.parent.parent
            rules_file = project_root / "config" / "rules.json"
            print(rules_file)
        
        self.rules_file = Path(rules_file)
        self._ensure_rules_file_exists()
    
    def _ensure_rules_file_exists(self):
        """Ensure the rules file and directory exist"""
        if not self.rules_file.parent.exists():
            self.rules_file.parent.mkdir(parents=True, exist_ok=True)
            configured_logger.info(f"Created rules directory: {self.rules_file.parent}")
        
        if not self.rules_file.exists():
            # Create default rules file
            default_rules = self._get_default_rules()
            self.save_rules(default_rules)
            configured_logger.info(f"Created default rules file: {self.rules_file}")
    
    def _get_default_rules(self) -> List[Dict[str, Any]]:
        """Get default rules from constants.py"""
        try:
            from src.config.constants import rules
            return rules
        except ImportError:
            configured_logger.warning("Could not import default rules from constants.py")
            return []
    
    def load_rules(self) -> List[Dict[str, Any]]:
        """
        Load rules from the JSON file.
        
        Returns:
            List of rule dictionaries
        """
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            rules = data.get("rules", [])

            configured_logger.info(f"Loaded {len(rules)} rules from {self.rules_file}")
            return rules
        
        except FileNotFoundError:
            configured_logger.error(f"Rules file not found: {self.rules_file}")
            return self._get_default_rules()
        
        except json.JSONDecodeError as e:
            configured_logger.error(f"Invalid JSON in rules file: {e}")
            return self._get_default_rules()
        
        except Exception as e:
            configured_logger.error(f"Error loading rules: {e}")
            return self._get_default_rules()
    
    def save_rules(self, rules: List[Dict[str, Any]], backup: bool = True) -> bool:
        """
        Save rules to the JSON file.
        
        Args:
            rules: List of rule dictionaries to save
            backup: Whether to create a backup of the existing file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup if requested and file exists
            if backup and self.rules_file.exists():
                backup_file = self.rules_file.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                import shutil
                shutil.copy2(self.rules_file, backup_file)
                configured_logger.info(f"Created backup: {backup_file}")
            
            # Prepare data structure
            data = {
                "rules": rules,
                "metadata": {
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "description": "Evaluation rules for job application screening"
                }
            }
            
            # Save to file
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            configured_logger.info(f"Saved {len(rules)} rules to {self.rules_file}")
            return True
        
        except Exception as e:
            configured_logger.error(f"Error saving rules: {e}")
            return False
    
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Add a new rule to the rules file.
        
        Args:
            rule: Rule dictionary to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rules = self.load_rules()
            rules.append(rule)
            return self.save_rules(rules)
        except Exception as e:
            configured_logger.error(f"Error adding rule: {e}")
            return False
    
    def update_rule(self, index: int, rule: Dict[str, Any]) -> bool:
        """
        Update a rule at the specified index.
        
        Args:
            index: Index of the rule to update
            rule: New rule dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rules = self.load_rules()
            if 0 <= index < len(rules):
                rules[index] = rule
                return self.save_rules(rules)
            else:
                configured_logger.error(f"Invalid rule index: {index}")
                return False
        except Exception as e:
            configured_logger.error(f"Error updating rule: {e}")
            return False
    
    def delete_rule(self, index: int) -> bool:
        """
        Delete a rule at the specified index.
        
        Args:
            index: Index of the rule to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rules = self.load_rules()
            if 0 <= index < len(rules):
                deleted_rule = rules.pop(index)
                configured_logger.info(f"Deleted rule: {deleted_rule}")
                return self.save_rules(rules)
            else:
                configured_logger.error(f"Invalid rule index: {index}")
                return False
        except Exception as e:
            configured_logger.error(f"Error deleting rule: {e}")
            return False
    
    def get_rule(self, index: int) -> Dict[str, Any]:
        """
        Get a specific rule by index.
        
        Args:
            index: Index of the rule to retrieve
            
        Returns:
            Rule dictionary or None if not found
        """
        try:
            rules = self.load_rules()
            if 0 <= index < len(rules):
                return rules[index]
            else:
                configured_logger.error(f"Invalid rule index: {index}")
                return None
        except Exception as e:
            configured_logger.error(f"Error getting rule: {e}")
            return None
    
    def validate_rule(self, rule: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate a rule structure.
        
        Args:
            rule: Rule dictionary to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        rule_type = rule.get("type")
        if not rule_type:
            return False, "Rule must have a 'type' field"
        
        # Validate based on rule type
        if rule_type in ["and", "or", "optional_and"]:
            if "rules" not in rule:
                return False, f"{rule_type} rule must have 'rules' field"
            if not isinstance(rule["rules"], list):
                return False, f"{rule_type} 'rules' must be a list"
        
        elif rule_type == "unstructured":
            if "field" not in rule:
                return False, "Unstructured rule must have 'field'"
            if "evaluation_criteria" not in rule:
                return False, "Unstructured rule must have 'evaluation_criteria'"
        
        else:
            # Field-based rules
            if "field" not in rule:
                return False, f"{rule_type} rule must have 'field'"
        
        return True, ""
    
    def reset_to_defaults(self) -> bool:
        """
        Reset rules to default values.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            default_rules = self._get_default_rules()
            return self.save_rules(default_rules, backup=True)
        except Exception as e:
            configured_logger.error(f"Error resetting to defaults: {e}")
            return False


# Global rules manager instance
_rules_manager = None


def get_rules_manager() -> RulesManager:
    """Get the global rules manager instance"""
    global _rules_manager
    if _rules_manager is None:
        _rules_manager = RulesManager()
    return _rules_manager


def load_rules_from_file() -> List[Dict[str, Any]]:
    """Convenience function to load rules"""
    return get_rules_manager().load_rules()
