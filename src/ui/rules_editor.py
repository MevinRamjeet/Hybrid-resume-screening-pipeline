"""
Rules Editor UI Component for Gradio
"""
import gradio as gr
import json
from typing import Dict, Any, List
from .utils import call_api_endpoint


async def load_rules(api_url: str) -> tuple[str, str]:
    """
    Load current rules from the API.
    
    Args:
        api_url: Base URL of the API server
        
    Returns:
        Tuple of (formatted_rules_json, status_message)
    """
    try:
        response = await call_api_endpoint(
            endpoint="/api/v1/rules",
            base_url=api_url,
            method="GET"
        )
        
        if response.get("error"):
            return "", f"❌ Error: {response.get('message', 'Failed to load rules')}"
        
        rules = response.get("rules", [])
        rules_json = json.dumps(rules, indent=2)
        
        total = response.get("total_rules", len(rules))
        structured = response.get("structured_count", 0)
        unstructured = response.get("unstructured_count", 0)
        
        status = f"✅ Loaded {total} rules ({structured} structured, {unstructured} unstructured)"
        return rules_json, status
    
    except Exception as e:
        return "", f"❌ Error loading rules: {str(e)}"


async def save_rules(rules_json: str, api_url: str) -> str:
    """
    Save updated rules to the API.
    
    Args:
        rules_json: JSON string containing rules
        api_url: Base URL of the API server
        
    Returns:
        Status message
    """
    try:
        # Parse JSON
        try:
            rules = json.loads(rules_json)
        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON: {str(e)}"
        
        # Validate it's a list
        if not isinstance(rules, list):
            return "❌ Rules must be a JSON array (list)"
        
        # Save rules
        response = await call_api_endpoint(
            endpoint="/api/v1/rules",
            method="PUT",
            data=rules,
            base_url=api_url
        )
        
        if response.get("error"):
            return f"❌ Error: {response.get('message', 'Failed to save rules')}"
        
        total = response.get("total_rules", 0)
        return f"✅ Successfully saved {total} rules. Backup created."
    
    except Exception as e:
        return f"❌ Error saving rules: {str(e)}"


async def add_new_rule(rule_json: str, api_url: str) -> tuple[str, str]:
    """
    Add a new rule.
    
    Args:
        rule_json: JSON string containing the new rule
        api_url: Base URL of the API server
        
    Returns:
        Tuple of (updated_rules_json, status_message)
    """
    try:
        # Parse JSON
        try:
            rule = json.loads(rule_json)
        except json.JSONDecodeError as e:
            return "", f"❌ Invalid JSON: {str(e)}"
        
        # Add rule
        response = await call_api_endpoint(
            endpoint="/api/v1/rules",
            method="POST",
            data=rule,
            base_url=api_url
        )
        
        if response.get("error"):
            return "", f"❌ Error: {response.get('message', 'Failed to add rule')}"
        
        # Reload rules
        rules_json, _ = await load_rules(api_url)
        
        index = response.get("index", 0)
        total = response.get("total_rules", 0)
        return rules_json, f"✅ Rule added at index {index}. Total rules: {total}"
    
    except Exception as e:
        return "", f"❌ Error adding rule: {str(e)}"


async def delete_rule_by_index(index: int, api_url: str) -> tuple[str, str]:
    """
    Delete a rule by index.
    
    Args:
        index: Index of the rule to delete
        api_url: Base URL of the API server
        
    Returns:
        Tuple of (updated_rules_json, status_message)
    """
    try:
        # Delete rule
        response = await call_api_endpoint(
            endpoint=f"/api/v1/rules/{index}",
            method="DELETE",
            base_url=api_url
        )
        
        if response.get("error"):
            return "", f"❌ Error: {response.get('message', 'Failed to delete rule')}"
        
        # Reload rules
        rules_json, _ = await load_rules(api_url)
        
        total = response.get("total_rules", 0)
        return rules_json, f"✅ Rule at index {index} deleted. Total rules: {total}"
    
    except Exception as e:
        return "", f"❌ Error deleting rule: {str(e)}"


async def reset_to_defaults(api_url: str) -> tuple[str, str]:
    """
    Reset rules to default values.
    
    Args:
        api_url: Base URL of the API server
        
    Returns:
        Tuple of (updated_rules_json, status_message)
    """
    try:
        response = await call_api_endpoint(
            endpoint="/api/v1/rules/reset",
            method="POST",
            base_url=api_url
        )
        
        if response.get("error"):
            return "", f"❌ Error: {response.get('message', 'Failed to reset rules')}"
        
        # Reload rules
        rules_json, _ = await load_rules(api_url)
        
        total = response.get("total_rules", 0)
        return rules_json, f"✅ Rules reset to defaults. Total rules: {total}. Backup created."
    
    except Exception as e:
        return "", f"❌ Error resetting rules: {str(e)}"


def create_rules_editor_tab(api_url_state: gr.State) -> gr.Tab:
    """
    Create the rules editor tab.
    
    Args:
        api_url_state: Gradio state for API URL
        
    Returns:
        Gradio Tab component
    """
    with gr.Tab("⚙️ Edit Rules") as tab:
        gr.Markdown("""
        ### Rules Editor
        Edit, add, or delete evaluation rules. Changes are saved to `config/rules.json`.
        
        ⚠️ **Warning**: Editing rules affects all future evaluations. A backup is created automatically.
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("#### Current Rules (JSON)")
                
                rules_editor = gr.Code(
                    label="Rules Configuration",
                    language="json",
                    lines=25,
                    value=""
                )
                
                with gr.Row():
                    load_btn = gr.Button("📥 Load Rules", variant="secondary")
                    save_btn = gr.Button("💾 Save Rules", variant="primary")
                    reset_btn = gr.Button("🔄 Reset to Defaults", variant="secondary")
                
                status_output = gr.Markdown("Click 'Load Rules' to view current configuration")
            
            with gr.Column(scale=1):
                gr.Markdown("#### Quick Actions")
                
                gr.Markdown("**Add New Rule:**")
                new_rule_input = gr.Code(
                    label="New Rule (JSON)",
                    language="json",
                    lines=10,
                    value='''{
  "field": "example_field",
  "type": "exists",
  "description": "Field must exist"
}'''
                )
                add_rule_btn = gr.Button("➕ Add Rule", variant="primary")
                
                gr.Markdown("**Delete Rule:**")
                delete_index_input = gr.Number(
                    label="Rule Index to Delete",
                    value=0,
                    precision=0
                )
                delete_rule_btn = gr.Button("🗑️ Delete Rule", variant="stop")
                
                gr.Markdown("""
                ---
                ### 📖 Rule Types Reference
                
                **Common Types:**
                - `exists` - Field must be present
                - `exact_match` - Must match exact value
                - `one_of` - Must be one of values
                - `range` - Numeric range (min/max)
                - `regex` - Pattern matching
                - `boolean` - True/false value
                - `and` / `or` - Logical combinations
                - `unstructured` - AI evaluation
                
                **Example:**
                ```json
                {
                  "field": "age",
                  "type": "range",
                  "min": 18,
                  "max": 45,
                  "description": "Age requirement"
                }
                ```
                """)
        
        # Event handlers
        load_btn.click(
            fn=load_rules,
            inputs=[api_url_state],
            outputs=[rules_editor, status_output]
        )
        
        save_btn.click(
            fn=save_rules,
            inputs=[rules_editor, api_url_state],
            outputs=[status_output]
        )
        
        add_rule_btn.click(
            fn=add_new_rule,
            inputs=[new_rule_input, api_url_state],
            outputs=[rules_editor, status_output]
        )
        
        delete_rule_btn.click(
            fn=delete_rule_by_index,
            inputs=[delete_index_input, api_url_state],
            outputs=[rules_editor, status_output]
        )
        
        reset_btn.click(
            fn=reset_to_defaults,
            inputs=[api_url_state],
            outputs=[rules_editor, status_output]
        )
    
    return tab
