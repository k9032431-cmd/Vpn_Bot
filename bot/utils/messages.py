from __future__ import annotations

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message


async def show_text(callback: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> None:
    """Replace the callback's message with a text screen.

    The main menu is a photo message (welcome banner), and Telegram
    rejects turning a photo message into a text one via edit_text --
    delete-and-resend handles that case, edit_text is kept for a plain
    text message already in place.
    """
    message = callback.message
    if message.photo:
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(text, reply_markup=reply_markup)
    else:
        await message.edit_text(text, reply_markup=reply_markup)


async def track_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    """Stashes the callback's own message id in FSM state, right after a
    callback step edits its way into a prompt that now waits for the user
    to type something. The upcoming text-message handler reads this back
    (via advance_screen) so it can keep editing the same screen instead of
    stacking a new bot message under the user's reply -- without it, every
    wizard's chat history fills up with the trail of old prompts it walked
    through to get to the current step."""
    await state.update_data(prompt_message_id=callback.message.message_id)


class TrackedMessage:
    """A (bot, chat_id, message_id) handle that keeps exposing `.edit_text`
    the same way a real aiogram Message does, for the rest of a handler
    that wants to keep editing the screen `advance_screen` just produced
    without round-tripping through FSM state again (e.g. a multi-step
    "connecting... / error / success" sequence right after the last typed
    field)."""

    def __init__(self, bot, chat_id: int, message_id: int) -> None:
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = message_id

    async def edit_text(self, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> "TrackedMessage":
        await self.bot.edit_message_text(
            text, chat_id=self.chat_id, message_id=self.message_id, reply_markup=reply_markup
        )
        return self


async def advance_screen(
    message: Message, state: FSMContext, text: str, reply_markup: InlineKeyboardMarkup | None = None
) -> TrackedMessage:
    """Moves a wizard's single on-screen prompt forward, in a text-message
    handler (CallbackQuery steps just use edit_text directly -- this is
    only for steps reached by the user typing a reply).

    `message` is the user's own reply that triggered this step -- deleted
    here, the same cleanup already used for passwords/secrets, now applied
    to every step so a stray hostname or IP left behind doesn't look like
    this is the one field worth hiding. The bot's previous prompt (its
    message id stashed by the step that showed it, via track_prompt or a
    prior advance_screen call) is edited in place; if that's not possible
    -- expired, deleted, or this is the very first prompt in the flow --
    a new message is sent instead. Stores the resulting message's id back
    into state so the *next* step can do the same, and returns a
    TrackedMessage handle for the rest of *this* step to keep editing.
    """
    try:
        await message.delete()
    except Exception:
        pass

    data = await state.get_data()
    prompt_message_id = data.get("prompt_message_id")
    bot = message.bot
    chat_id = message.chat.id

    edited = False
    if prompt_message_id:
        try:
            await bot.edit_message_text(text, chat_id=chat_id, message_id=prompt_message_id, reply_markup=reply_markup)
            edited = True
        except Exception:
            edited = False

    if not edited:
        sent = await bot.send_message(chat_id, text, reply_markup=reply_markup)
        prompt_message_id = sent.message_id

    await state.update_data(prompt_message_id=prompt_message_id)
    return TrackedMessage(bot, chat_id, prompt_message_id)


async def show_screen(
    source: CallbackQuery | Message, state: FSMContext, text: str, reply_markup: InlineKeyboardMarkup | None = None
) -> None:
    """Shows a wizard's next step from a call site reachable both by a
    button and by the user typing a reply -- e.g. an auth-method choice
    that can come from a "password" button (a CallbackQuery; its own
    message is already the current screen, just edited in place) or from
    pasting an SSH key as a text reply (a Message; advance_screen keeps
    editing the same tracked screen instead of stacking a new one under
    it). Picks the right behavior from the type of `source`."""
    if isinstance(source, CallbackQuery):
        await source.message.edit_text(text, reply_markup=reply_markup)
    else:
        await advance_screen(source, state, text, reply_markup=reply_markup)
