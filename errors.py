from discord.ext.commands import CommandError


class MyError(CommandError):
    def __init__(self, message: str) -> None:
        self.message = message


class ChannelAlreadyExists(MyError):

    def __init__(self):
        super().__init__('`chat-bot` channel already exists.')


class ChannelFailedToCreate(MyError):

    def __init__(self):
        super().__init__('Failed to create `chat-bot` channel.')


class Timeout(MyError):

    def __init__(self):
        super().__init__('Interrupted because the process was taking too long')