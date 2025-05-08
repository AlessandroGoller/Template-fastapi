echo "Ruff checks"
ruff check app || goto :error

echo "Run type checking"
mypy --install-types --non-interactive app || goto :error

echo "Run Vermin"
vermin --no-tips -t="3.11-" --violations app || goto :error

echo "Run pip-audit"
pip-audit --desc on --progress-spinner off || goto :error

echo "check alembic is updated"
alembic check || goto :error

echo "Run pylint"
pylint app || goto :error

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%

:end
echo Pipeline run succesfully