from fastapi import FastAPI, Request
import contextlib
import time
import threading
import uvicorn
from os import path
from app.client import spotify_oauth
from fastapi.responses import HTMLResponse
from app import TEMP_PATH

app = FastAPI()

@app.get("/callback")
async def root(code: str, state: str, request: Request):
    spotify_oauth.parse_auth_response_url(str(request.url))
    spotify_oauth.get_access_token(code)
    with open(path.join(TEMP_PATH, 'kill_thread'), 'w'):
        pass

    html_content = """
    <html>
    <head>
        <title>Close Window</title>
        <script>
            // JavaScript code to close the window
            function closeWindow() {
                window.close();
            }

            // Close the window after 3 seconds (you can adjust the delay)
            setTimeout(closeWindow, 3000);
        </script>
    </head>
    <body>
        <h1>Window will close in 3 seconds...</h1>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


class Server(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()
