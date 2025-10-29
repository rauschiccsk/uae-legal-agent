@echo off
echo Installing config module dependencies...
cd C:/Development/uae-legal-agent
pip install pydantic pydantic-settings python-dotenv

echo.
echo Running config module tests...
python -m pytest tests/test_config.py -v

echo.
echo Test run complete.
pause