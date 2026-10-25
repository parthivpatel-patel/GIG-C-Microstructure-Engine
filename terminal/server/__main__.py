"""python -m terminal.server; localhost only by default, one worker required."""
import uvicorn

if __name__ == '__main__':
    uvicorn.run('terminal.server.app:app', host='127.0.0.1', port=8787, workers=1,
                ws_max_size=4096, ws_max_queue=4, timeout_keep_alive=5,
                limit_concurrency=32, h11_max_incomplete_event_size=8192)
