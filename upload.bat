echo "upgrade twine"
pip install --upgrade twine

echo "install package"
pip install .

echo "build package"
python setup.py sdist bdist_wheel

echo "upload package"
twine.exe upload dist/* --config-file .pypirc