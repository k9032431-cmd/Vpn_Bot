from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.main_menu import back_keyboard
from bot.keyboards.crypt import (
    crypt_action_keyboard,
    crypt_cancel_keyboard,
    crypt_result_keyboard,
    crypt_vpn_keyboard,
)
from bot.services.happ_api import HappAPIError, happ_encrypt_link
from bot.states.crypt import CryptStates
from bot.texts import crypt as texts

router = Router(name="crypt")


@router.callback_query(F.data == "menu:crypt")
async def cb_crypt_menu(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.message.edit_text(texts.choose_action_text(lang), reply_markup=crypt_action_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "crypt:action:decrypt")
async def cb_crypt_decrypt(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.message.edit_text(texts.decrypt_soon_text(lang), reply_markup=back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "crypt:action:encrypt")
async def cb_crypt_encrypt(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await callback.message.edit_text(texts.choose_vpn_text(lang), reply_markup=crypt_vpn_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "crypt:vpn:happ")
async def cb_crypt_vpn_happ(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(CryptStates.waiting_subscription_url)
    await callback.message.edit_text(texts.waiting_url_text(lang), reply_markup=crypt_cancel_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "crypt:cancel")
async def cb_crypt_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.message.edit_text(texts.cancelled_text(lang), reply_markup=back_keyboard(lang))
    await callback.answer()


@router.message(CryptStates.waiting_subscription_url)
async def process_crypt_subscription_url(message: Message, state: FSMContext, lang: str) -> None:
    url = message.text.strip() if message.text else ""
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.answer(texts.invalid_url_text(lang), reply_markup=crypt_cancel_keyboard(lang))
        return

    await message.bot.send_chat_action(message.chat.id, "typing")
    try:
        link = await happ_encrypt_link(url)
    except HappAPIError as exc:
        await message.answer(texts.error_text(lang, str(exc)), reply_markup=crypt_cancel_keyboard(lang))
        return

    await state.clear()
    await message.answer(texts.result_text(lang, link), reply_markup=crypt_result_keyboard(lang))
