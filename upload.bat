echo "clear dist directory"
rmdir /S /Q dist
mkdir dist

echo "upgrade twine"
pip install --upgrade twine

echo "install package"
pip install .

echo "build package"
py -m build --wheel

echo "upload package"
twine.exe upload dist/* --config-file .pypirc