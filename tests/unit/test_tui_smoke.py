import pytest
from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput
from jup.commands.tui import async_tui_main


@pytest.mark.asyncio
async def test_tui_startup():
    """
    Smoke test to ensure the TUI can start up and shutdown without crashing.
    """
    with create_pipe_input() as inp:
        # Pre-send 'q' to immediately quit the application
        inp.send_text("q")

        with create_app_session(input=inp, output=DummyOutput()):
            # async_tui_main() returns the result of app.run_async()
            result = await async_tui_main()
            assert result is None
