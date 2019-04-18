"""
The MIT License (MIT)

Copyright (c) 2017-2018 Nariman Safiulin

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import asyncio

import discord

from .constants import EventType
from .context import Context
from .middleware import Middleware


class Client(discord.Client):
    """Wrapper around default library client.

    Parameters
    ----------
    root_middleware : :class:`Middleware`
        A middleware to run on new events.
    """

    def __init__(self, root_middleware: Middleware, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root_middleware = root_middleware

    async def default_next_callable(ctx, *args, **kwargs):  # noqa: D401
        """Default callable as the `next` parameter.

        Ideally, it should not be called due to it is just a "right" argument
        for event handlers that should ignore next callables.
        """
        pass

    def dispatch(self, event, *args, **kwargs):  # noqa: D401
        """Wrapper around default event dispatcher for a client."""
        super().dispatch(event, *args, **kwargs)

        try:
            event_type = EventType(event)
        except ValueError:
            event_type = EventType.UNKNOWN
        #
        ctx = Context(self, event_type, *args, **kwargs)
        asyncio.ensure_future(
            self._run_event(
                self.root_middleware.run,
                event,
                ctx=ctx,
                next=self.default_next_callable,
            ),
            loop=self.loop,
        )
