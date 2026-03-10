import discord
from discord.ext import commands

# ==========================================
# 1. إعداد واجهة القائمة المنسدلة (Select Menu)
# ==========================================
class ReportSelect(discord.ui.Select):
    def __init__(self):
        # هنا نحدد الخيارات التي ستظهر للاعب في القائمة
        options = [
            discord.SelectOption(label="مخالفة قوانين", description="للإبلاغ عن لاعب خالف القوانين", emoji="🚨"),
            discord.SelectOption(label="مشكلة تقنية", description="للإبلاغ عن خلل أو خطأ في السيرفر", emoji="⚙️"),
            discord.SelectOption(label="شكوى إدارية", description="تقديم شكوى بخصوص طاقم الإدارة", emoji="📋")
        ]
        # إعداد القائمة المنسدلة (النص الافتراضي، وأقل وأكثر عدد للاختيار)
        super().__init__(placeholder="اختر سبب البلاغ من هنا...", min_values=1, max_values=1, options=options, custom_id="report_select_menu")

    # هذه الدالة تعمل فوراً عندما يختار اللاعب خياراً من القائمة
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        # جلب السبب الذي اختاره اللاعب
        reason = self.values[0]

        # تنظيف الاسم ليتوافق مع شروط ديسكورد للقنوات النصية (استبدال المسافات بشرطات)
        safe_reason = reason.replace(" ", "-")
        channel_name = f"{user.name}-{safe_reason}"

        # إعداد الصلاحيات للقناة الجديدة
        overwrites = {
            # منع الجميع من رؤية القناة
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            # السماح لصاحب التذكرة برؤية القناة والكتابة فيها
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            # (يمكننا لاحقاً إضافة رتبة الإدارة هنا لتتمكن من رؤية البلاغ)
        }

        # إنشاء القناة النصية
        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)

        # إرسال رسالة للاعب تفيد بنجاح العملية (تظهر له وحده)
        await interaction.response.send_message(f"✅ تم فتح تذكرة البلاغ بنجاح: {ticket_channel.mention}", ephemeral=True)

        # إرسال رسالة ترحيبية داخل قناة التذكرة نفسها
        await ticket_channel.send(f"أهلاً بك {user.mention}،\nلقد قمت بفتح بلاغ بخصوص: **{reason}**.\nالرجاء كتابة تفاصيل المشكلة هنا وسيقوم فريق الدعم بالرد عليك في أقرب وقت.")

# ==========================================
# 2. إعداد الحاوية (View) التي ستحمل القائمة
# ==========================================
class ReportView(discord.ui.View):
    def __init__(self):
        # timeout=None تجعل الأزرار والقوائم تعمل دائماً حتى بعد إعادة تشغيل البوت
        super().__init__(timeout=None)
        self.add_item(ReportSelect())

# ==========================================
# 3. إعداد البوت الأساسي
# ==========================================
class MyBot(commands.Bot):
    def __init__(self):
        # إعطاء البوت الصلاحيات اللازمة لقراءة الرسائل وإنشاء القنوات
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    # هذه الدالة تعمل عند تشغيل البوت لتسجيل القائمة المنسدلة في النظام
    async def setup_hook(self):
        self.add_view(ReportView())

bot = MyBot()

@bot.event
async def on_ready():
    print(f"تم تشغيل البوت بنجاح! مسجل باسم: {bot.user}")

# أمر لإنشاء لوحة البلاغات (يستخدمه الإداري فقط)
@bot.command()
@commands.has_permissions(administrator=True) # يتطلب صلاحية مسؤول
async def setup_reports(ctx):
    # إنشاء رسالة اللوحة (Embed)
    embed = discord.Embed(
        title="نظام البلاغات والدعم",
        description="إذا واجهتك أي مشكلة أو أردت تقديم بلاغ، يرجى اختيار السبب المناسب من القائمة بالأسفل لفتح تذكرة خاصة بك.",
        color=discord.Color.red()
    )
    # إرسال اللوحة مع القائمة المنسدلة
    await ctx.send(embed=embed, view=ReportView())

# ضع توكن البوت الخاص بك هنا (بين علامتي التنصيص)

bot.run("MTQ4MDk1OTY3OTgxODQ5ODE2MA.GHmYBT.oTmqVDRFIy5qYUsUHHyAe_rWwQdJ2EKBJhK5ww")

