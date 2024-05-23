from fastapi import FastAPI, Request
import contextlib
import time
import threading
from threading import Event
import uvicorn
from fastapi.responses import HTMLResponse
from app.core.client import Client


app = FastAPI()
ExitEvent = Event()


@app.get("/callback")
async def root(code: str, state: str, request: Request):
    client = Client()
    client.spotify_oauth.parse_auth_response_url(str(request.url))
    client.spotify_oauth.get_access_token(code)
    ExitEvent.clear()

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
