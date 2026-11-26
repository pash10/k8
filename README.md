# Local Kubernetes Deployment editor

Run `python -m pip install -r requirements.txt`, then `python YMAL/app.py`. Open http://127.0.0.1:5000. Run `python -m unittest discover -s YMAL -p 'test_*.py'` from the root.

This draft deliberately limits editing to six typed fields on the existing Deployment example. It uses a fixed autoescaped template, validates fields and CSRF tokens, and returns a YAML download instead of writing shared files. It does not accept arbitrary YAML uploads or deploy to a cluster. Full Kubernetes schema and admission validation remain separate tasks. Keep this prototype local; production hosting would require authentication, TLS, secure cookies and an appropriate WSGI server.

The example uses an unprivileged NGINX image (UID/GID 101), port 8080, read-only root filesystem, a bounded writable /tmp, no service-account token, dropped capabilities and RuntimeDefault seccomp. Create the example ConfigMap and namespace separately. The image tag is mutable; pin a verified digest for deployment. If changing the image or port in the editor, verify compatibility with UID 101 and the restricted runtime settings; the editor does not enforce an image allowlist or run admission checks. No cluster deployment is performed by the tests.
