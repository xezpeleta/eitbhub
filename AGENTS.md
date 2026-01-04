# Agent Preferences and Project Guidelines

## Development Tools

### Package Management
- **Use `uv` (from Astral)** for all Python dependency management and code execution
- Do NOT use `pip` or `pip install`
- `uv` is faster and more reliable for dependency resolution

### Common Commands

```bash
# Install dependencies
uv pip install -r requirements.txt

# Run Python scripts
uv run python script.py

# Or install in a virtual environment
uv venv
source .venv/bin/activate  # On Linux/Mac
uv pip install -r requirements.txt
```

## Project-Specific Notes

### Platform Documentation
- Each platform has its own documentation in `platforms/{platform_name}/`
- See platform-specific README.md files for authentication details
- API documentation is in `platforms/{platform_name}/API.md`

### Environment Variables
- Store credentials in `.env` file (never commit this!)
- Use `.env.example` as template
- For passwords with special characters, see "Special Characters in .env" section below

## Special Characters in .env Files

When your password contains special characters like `]`, `"`, `'`, etc.:

**✓ CORRECT - No quotes needed:**
```bash
PRIMERAN_PASSWORD=my]pass"word
```

**✗ WRONG - Don't add quotes:**
```bash
PRIMERAN_PASSWORD="my]pass"word"  # This will include the quotes in the password!
```

**Rules:**
- The value is everything after `=` until the end of the line
- No quotes, escaping, or special handling needed
- Spaces are preserved
- Empty lines and `#` comments are ignored

**Example with complex password:**
```bash
# Good - password with special chars
PRIMERAN_USERNAME=user@example.com
PRIMERAN_PASSWORD=P@ss[]w"ord'123!

# The password is exactly: P@ss[]w"ord'123!
```

## Development Workflow

1. Use `uv` for all Python operations
2. Keep `.env` file secure and gitignored
3. Test with sample data before production runs
4. Document any API changes in platform-specific API.md files
5. When adding new platforms, follow the structure in `platforms/primeran/`

---

*Last updated: 2026-01-04*
