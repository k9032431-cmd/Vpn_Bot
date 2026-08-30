from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main_menu import back_keyboard
from bot.keyboards.whois import whois_again_keyboard, whois_cancel_keyboard
from bot.services.whois_api import WhoisAPIError, is_domain, is_ip, lookup_domain, lookup_ip
from bot.states.whois import WhoisStates
from bot.texts import whois as texts

router = Router(name="whois")


@router.callback_query(F.data == "menu:whois")
async def cb_whois_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await state.set_state(WhoisStates.waiting_query)
    await callback.message.edit_text(texts.prompt_text(lang), reply_markup=whois_cancel_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "whois:cancel")
async def cb_whois_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.message.edit_text(texts.cancelled_text(lang), reply_markup=back_keyboard(lang))
    await callback.answer()


@router.message(WhoisStates.waiting_query)
async def process_whois_query(message: Message, state: FSMContext, lang: str) -> None:
    query = message.text.strip() if message.text else ""
    query = query.removeprefix("http://").removeprefix("https://").split("/")[0].strip()

    if not query or not (is_ip(query) or is_domain(query)):
        await message.answer(texts.invalid_input_text(lang), reply_markup=whois_cancel_keyboard(lang))
        return

    status_message = await message.answer(texts.looking_up_text(lang))
    try:
        if is_ip(query):
            info = await lookup_ip(query)
            result_text = texts.ip_result_text(lang, query, info)
        else:
            info = await lookup_domain(query)
            result_text = texts.domain_result_text(lang, query, info)
    except WhoisAPIError as exc:
        await status_message.edit_text(texts.error_text(lang, str(exc)), reply_markup=whois_again_keyboard(lang))
        return

    await state.clear()
    await status_message.edit_text(result_text, reply_markup=whois_again_keyboard(lang))
