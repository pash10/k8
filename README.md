# Local Kubernetes Deployment editor

Run `python -m pip install -r requirements.txt`, then `python YMAL/app.py`. Open http://127.0.0.1:5000. Run `python -m unittest discover -s YMAL -p 'test_*.py'` from the root.

This draft deliberately limits editing to six typed fields on the existing Deployment example. It uses a fixed autoescaped template, validates fields and CSRF tokens, and returns a YAML download instead of writing shared files. It does not accept arbitrary YAML uploads or deploy to a cluster. Full Kubernetes schema and admission validation remain separate tasks. Keep this prototype local; production hosting would require authentication, TLS, secure cookies and an appropriate WSGI server.
