#!/bin/bash
echo "AAROGYA v1 Deploy Check..."
pytest tests/ -v
if [ $? -eq 0 ]; then
    echo " All tests passed!"
    echo "Ready to deploy!"
else
    echo " Tests failed!"
    exit 1
fi
