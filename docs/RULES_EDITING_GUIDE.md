# 📝 Rules Editing Guide

**How to Customize Screening Criteria**

---

## Overview

The screening system now supports **editable rules**! You can customize what gets checked without modifying code. All rules are stored in `config/rules.json` and can be edited through the web interface or directly.

---

## 🎯 Quick Start

### Option 1: Web Interface (Easiest)

1. **Start the system:**
   ```bash
   python run_full_stack.py
   ```

2. **Open your browser** to http://127.0.0.1:7860

3. **Go to the "⚙️ Edit Rules" tab**

4. **Click "📥 Load Rules"** to see current rules

5. **Edit the JSON** directly in the editor

6. **Click "💾 Save Rules"** to apply changes

### Option 2: Edit File Directly

1. Open `config/rules.json` in a text editor

2. Modify the rules array

3. Save the file

4. Restart the system (changes apply immediately on next evaluation)

---

## 📖 Understanding Rules

### Rule Structure

Every rule has these basic components:

```json
{
  "field": "age",
  "type": "range",
  "min": 18,
  "max": 45,
  "description": "Age must be between 18 and 45"
}
```

- **field**: Which application field to check
- **type**: What kind of check to perform
- **Additional properties**: Depends on the rule type
- **description**: Human-readable explanation (optional but recommended)

---

## 🔧 Rule Types

### 1. **Exact Match**
Field must match a specific value exactly.

```json
{
  "field": "nationality",
  "type": "exact_match",
  "value": "Mauritian",
  "description": "Must be Mauritian citizen"
}
```

### 2. **One Of** (Multiple Options)
Field must be one of the allowed values.

```json
{
  "field": "nationality",
  "type": "one_of",
  "values": ["Mauritian", "Permanent Resident"],
  "description": "Must be Mauritian or PR"
}
```

### 3. **Range** (Numbers)
Numeric value must be within a range.

```json
{
  "field": "age",
  "type": "range",
  "min": 21,
  "max": 50,
  "description": "Age between 21 and 50"
}
```

### 4. **Minimum/Maximum**
Check only minimum or maximum value.

```json
{
  "field": "work_experience_years",
  "type": "min",
  "value": 3,
  "description": "At least 3 years experience"
}
```

### 5. **Regex** (Pattern Matching)
Validate format using regular expressions.

```json
{
  "field": "email",
  "type": "regex",
  "pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$",
  "description": "Valid email format"
}
```

**Common Patterns:**
- Email: `^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$`
- Phone (7-8 digits): `^[0-9]{7,8}$`
- Date (YYYY-MM-DD): `^\\d{4}-\\d{2}-\\d{2}$`
- ID Number: `^[A-Z0-9]{14,20}$`

### 6. **Exists**
Field must be present and not null.

```json
{
  "field": "post_applied_for",
  "type": "exists",
  "description": "Position must be specified"
}
```

### 7. **Boolean**
Field must be true or false.

```json
{
  "field": "court_conviction",
  "type": "boolean",
  "value": false,
  "description": "No court convictions"
}
```

### 8. **String Contains**
String must contain specific values.

```json
{
  "field": "residential_address",
  "type": "string_contains",
  "values": ["Road", "Street", "Avenue"],
  "case_insensitive": true,
  "description": "Address must include street type"
}
```

### 9. **Length Check**
String length validation.

```json
{
  "field": "residential_address",
  "type": "length_check",
  "min_length": 10,
  "max_length": 200,
  "description": "Address must be 10-200 characters"
}
```

### 10. **Array Length**
Array must have minimum/maximum items.

```json
{
  "field": "degree_qualifications",
  "type": "array_length",
  "min_length": 1,
  "description": "At least one degree required"
}
```

### 11. **AND** (All Must Pass)
All sub-rules must pass.

```json
{
  "type": "and",
  "rules": [
    {"field": "post_applied_for", "type": "exists"},
    {"field": "ministry_department", "type": "exists"}
  ],
  "description": "Application info must be complete"
}
```

### 12. **OR** (At Least One Must Pass)
At least one sub-rule must pass.

```json
{
  "type": "or",
  "rules": [
    {"field": "phone_mobile", "type": "exists"},
    {"field": "phone_home", "type": "exists"}
  ],
  "description": "At least one phone number required"
}
```

### 13. **Unstructured** (AI Evaluation)
AI evaluates qualitative content.

```json
{
  "field": "work_experience",
  "type": "unstructured",
  "description": "Work experience",
  "evaluation_criteria": "Assess relevance and quality of work experience"
}
```

---

## 💡 Common Examples

### Change Age Range

**Current:**
```json
{"field": "age", "type": "range", "min": 18, "max": 45}
```

**Change to 21-50:**
```json
{"field": "age", "type": "range", "min": 21, "max": 50}
```

### Add Nationality Options

**Current:**
```json
{"field": "nationality", "type": "exact_match", "value": "Mauritian"}
```

**Allow Multiple:**
```json
{
  "field": "nationality",
  "type": "one_of",
  "values": ["Mauritian", "Permanent Resident", "Work Permit Holder"]
}
```

### Require Minimum Experience

**Add New Rule:**
```json
{
  "field": "work_experience_years",
  "type": "min",
  "value": 5,
  "description": "Minimum 5 years experience required"
}
```

### Make Field Optional

**Remove the rule** or use **optional_and**:
```json
{
  "type": "optional_and",
  "rules": [
    {"field": "optional_field", "type": "exists"}
  ]
}
```

---

## 🛠️ Using the Web Interface

### Load Rules
1. Click "📥 Load Rules"
2. Current rules appear in JSON format
3. Status shows rule count

### Edit Rules
1. Modify the JSON directly in the editor
2. Add, remove, or change rules
3. Ensure valid JSON syntax

### Save Rules
1. Click "💾 Save Rules"
2. System validates your changes
3. Backup created automatically
4. Changes apply to all future evaluations

### Add Single Rule
1. Enter rule JSON in "New Rule" box
2. Click "➕ Add Rule"
3. Rule appended to end of list

### Delete Rule
1. Find the rule index (0-based)
2. Enter index in "Rule Index to Delete"
3. Click "🗑️ Delete Rule"

### Reset to Defaults
1. Click "🔄 Reset to Defaults"
2. Confirms action
3. Restores original rules
4. Creates backup of current rules

---

## 🔍 API Endpoints

For programmatic access:

### Get All Rules
```bash
GET /api/v1/rules
```

### Update All Rules
```bash
PUT /api/v1/rules
Body: [array of rules]
```

### Add Rule
```bash
POST /api/v1/rules
Body: {rule object}
```

### Update Specific Rule
```bash
PUT /api/v1/rules/{index}
Body: {rule object}
```

### Delete Rule
```bash
DELETE /api/v1/rules/{index}
```

### Get Specific Rule
```bash
GET /api/v1/rules/{index}
```

### Reset to Defaults
```bash
POST /api/v1/rules/reset
```

---

## ⚠️ Important Notes

### Backups
- Automatic backup created before saving
- Backups stored as `config/rules.backup.YYYYMMDD_HHMMSS.json`
- Keep backups for recovery

### Validation
- Rules are validated before saving
- Invalid rules rejected with error message
- Check JSON syntax carefully

### Changes Apply Immediately
- New evaluations use updated rules
- No restart needed
- In-progress evaluations use old rules

### Testing
- Test rule changes with sample applications
- Verify expected behavior
- Keep backup before major changes

---

## 🆘 Troubleshooting

### "Invalid JSON" Error
- Check for missing commas
- Ensure all brackets match `{ }` and `[ ]`
- Validate quotes are correct `"`

### "Invalid Rule" Error
- Check required fields for rule type
- Verify field names match application schema
- Ensure values are correct type (string, number, etc.)

### Rules Not Applying
- Click "Load Rules" to verify changes saved
- Check `config/rules.json` file directly
- Restart system if needed

### Lost Rules
- Check backup files in `config/` directory
- Restore from backup: copy backup file to `rules.json`
- Use "Reset to Defaults" as last resort

---

## 📚 Best Practices

1. **Always add descriptions** - Helps understand rule purpose
2. **Test changes** - Verify with sample applications
3. **Keep backups** - Don't delete backup files
4. **Document changes** - Note why rules were modified
5. **Start small** - Change one rule at a time
6. **Validate syntax** - Use JSON validator if unsure

---

## 📞 Need Help?

- **Check syntax**: Use online JSON validator
- **Test rules**: Use sample applications
- **Restore backup**: Copy backup file to rules.json
- **Contact**: david.adediji@sil.mu

---

**Version 1.0.0** | Hybrid Resume Screening Pipeline
