from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main_menu import back_keyboard, main_menu_keyboard
from bot.keyboards.whois import whois_again_keyboard, whois_cancel_keyboard
from bot.services.whois_api import WhoisAPIError, is_domain, is_ip, lookup_domain, lookup_ip
from bot.states.whois import WhoisStates
from bot.texts import whois as texts
from bot.texts.main import welcome_text

router = Router(name="whois")


@router.callback_query(F.data == "menu:whois")
async def cb_whois_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await state.set_state(WhoisStates.waiting_query)
    # Always a new message, never an edit — a whois result is sent as a
    # reply to the query (see process_whois_query), and editing a reply
    # keeps Telegram's quoted-message header attached forever, which would
    # otherwise show up on every screen after it.
    await callback.message.answer(texts.prompt_text(lang), reply_markup=whois_cancel_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "whois:cancel")
async def cb_whois_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.message.answer(texts.cancelled_text(lang), reply_markup=back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "whois:home")
async def cb_whois_home(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.message.answer(welcome_text(lang), reply_markup=main_menu_keyboard(lang))
    await callback.answer()


@router.message(WhoisStates.waiting_query)
async def process_whois_query(message: Message, state: FSMContext, lang: str) -> None:
    query = message.text.strip() if message.text else ""
    query = query.removeprefix("http://").removeprefix("https://").split("/")[0].strip()

    if not query or not (is_ip(query) or is_domain(query)):
        await message.answer(texts.invalid_input_text(lang), reply_markup=whois_cancel_keyboard(lang))
        return

    # Answered as a reply to the query (rather than a separate/edited status
    # message) so Telegram shows the familiar quoted-query header above the
    # result — a typing indicator covers the wait instead of a placeholder.
    await message.bot.send_chat_action(message.chat.id, "typing")
    try:
        if is_ip(query):
            info = await lookup_ip(query)
            result_text = texts.ip_result_text(lang, info)
        else:
            info = await lookup_domain(query)
            result_text = texts.domain_result_text(lang, info)
    except WhoisAPIError as exc:
        await message.reply(texts.error_text(lang, str(exc)), reply_markup=whois_again_keyboard(lang))
        return

    await state.clear()
    await message.reply(result_text, reply_markup=whois_again_keyboard(lang))
