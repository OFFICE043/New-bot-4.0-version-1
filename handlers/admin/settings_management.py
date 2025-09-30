# handlers/admin/settings_management.py
# VIP бағасын, сипаттамасын өзгерту, ботты тоқтату/қосу логикасы
# ...
VIP_DESC_EDIT, VIP_PRICE_EDIT = range(2)

async def vip_desc_edit_start(update, context):
    # ...
    return VIP_DESC_EDIT
    
async def vip_desc_edit_receive(update, context):
    # ...
    return ConversationHandler.END

vip_settings_conv = ConversationHandler(...)
