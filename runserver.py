import os
from spectra import app

if os.environ.has_key('PORT'):
    port = int(os.environ['PORT'])
else:
    port = 5000

app.run("0.0.0.0", debug=True, port=port)
