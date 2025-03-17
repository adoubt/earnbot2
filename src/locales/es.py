LOCALES = {
    "start": """Nuestra empresa tiene un acuerdo con una agencia de publicidad para promocionar un vídeo en TikTok 📈
 
Por lo tanto, estamos dispuestos a pagar a cada usuario por ver vídeos cortos subidos por este bot.
 
⚠️ Tienes que ver los vídeos para ser recompensado. Los vídeos duran entre 10 y 15 segundos
 
💰 Puedes ganar hasta <b>15.000 Pesos</b> diariamente viendo vídeos
 
Para empezar, pulse el botón "<b>Ver vídeos y ganar dinero</b> 📺".""",
    "videos": """Nuestra empresa tiene un contrato con una agencia de publicidad que necesita promocionar vídeos en TikTok 📈

Por lo tanto, estamos dispuestos a pagar a cada uno de nuestros usuarios por ver vídeos cortos enviados por este bot.
 
⚠️ Tienes que ver el vídeo hasta el final para conseguir la recompensa. La duración del vídeo es de 10-15 segundos.
 
💰 Cada día puedes ganar hasta <b>15.000 Pesos</b> viendo vídeos
 
Pulse el botón "<b>Empezar a ver</b> 📺" para comenzar.""",
    "channel": """Únete a nuestro canal y te enseñaremos a ganar dinero!""",
    "rules": """Nuestra empresa tiene un acuerdo con una agencia de publicidad para promocionar un vídeo en TikTok 📈
 
Por lo tanto, estamos dispuestos a pagar a cada usuario por ver vídeos cortos subidos por este bot.
 
⚠️ Tienes que ver los vídeos para ser recompensado. Los vídeos duran entre 10 y 15 segundos
 
💰 Puedes ganar hasta <b>15.000 Pesos</b> diariamente viendo vídeos
 
Para empezar, pulse el botón "<b>Ver vídeos y ganar dinero</b> 📺".""",
    "profile": """Su saldo: <b>{balance} Pesos</b>
Número de amigos invitados: <b>{referrals}</b>
Usuarios invitados por tus amigos: <b>{rereferrals}</b>""",
    "withdraw_requested": """Ya tiene una solicitud de retirada activa.  Por favor, espere a que se procese.""",
    "withdraw_problems": """Desafortunadamente, experimentamos problemas técnicos, ¡nos disculpamos!
Su dinero será acreditado a su cuenta dentro de las 72 horas""",
    "withdraw_videos_threshold": """❗️ Debes ver al menos <b>5</b> vídeos para retirar fondos.

Haz clic en <b>Empezar a ver</b> 📺 y empieza ya.""",
    "withdraw_balance_threshold": """El saldo mínimo para retirar es  <b>75.000 Pesos</b>

Su saldo:  <b>{balance} Pesos</b>

Lamentablemente, este límite tuvo que fijarse para no sobrecargar el sistema con retiradas de pequeñas cantidades.""",
    "earn_more": """Nuestro proyecto es nuevo en telegram y necesitamos que todo el mundo nos conozca, por lo que estamos dispuestos a pagar por la publicidad 💵
 
🏆 Esta es tu link de enlace para las invitaciones 👇

 <a href="{link}">{link}</a>

 
✅ Copia el enlace y envíalo a tus amigos y conocidos
 
🏆 Por cada persona que visite el bot a través de tu enlace, obtienes <b>1500 Pesos</b>
 
Si alguien a quien invitas invita a nuevas personas, te pagan por usuario <b>750 Pesos</b>  
 
Así que puedes ganar sin límites!""",
    "card_number": """💳 Envíame los datos de tu cuenta <b>%PAYMENTOS%</b> de la que deseas retirar tus saldos""",
    "receive": """🎉 Has ganado  <b>{REWARD_RATE} Pesos</b> por ver el vídeo.

🤑 Su saldo:  <b>{new_balance} Pesos</b>""",
    
    "receive_abort_early": """⚠️Tienes que ver el vídeo en su totalidad⚠️""",
    "receive_abort_period": """⚠️ Hoy has cumplido con todos tus compromisos publicitarios y has recibido un premio! 😌

Puedes conseguir un nuevo contrato de publicidad durante: <b>{time_left}</b>

Si quieres ganar más, haz clic en el botón de abajo 👇""",
    "set_admin_empty": """❌ Empty request.
Example: `/set_admin durov`
!Username must be registered here!""",
    "set_admin_not_registred": """❌ {username} not registered or username is not displayed.""",
    "set_admin_succes": """✅ {username} is admin now 😎😎😎""",
    "admin_panel": """📌Admin Panel📌:

/ad - Рассылка                            
/all_videos 
/set_admin - Назначение админа (/set_admin durov)        
/stats
/start - swith to user panel
                           
<a href="https://github.com/adoubt/earnbot2">github</a>
<a href="https://github.com/users/adoubt/projects/7/views/1">project board</a>""",
    "ad": """<b>📢 Реклама</b>  

Перешли макет боту — он отправит его в • текущем режиме • 
 <b>all</b> — всем  
 <b>test</b> — только тебе  
 <b>admins</b> — админам  
 <b>off</b> — бот не реагирует (нужно для загрузки видео)  

*Несколько файлов сразу пока не поддерживается.*  

📊 <a href="{LOG_CHANNEL_LINK}">Логи отправки</a>""",
    "stats": """Registred users: {total_count}""",
    "all_videos_empty": """Nothing uploaded yet""",
    "all_videos": """All Videos ({total_videos}):""",
    "deleted_video": """'Deteted video_id: {video_id}""",
    "create_video_exists": """already exists""",
    "create_video_success": """👍🏿 Video successfully added!""",
    "exit_state": """no olvides aplicar""",
    "verify_succes": """Te has suscrito con éxito al canal ✅.

No es necesario que se dé de baja del canal si quiere retirar dinero.""",
    "verify_fail": """Todavía no estás suscrito al canal""",
    "email": """Introduzca su dirección de correo electrónico y le enviaremos la información.
por ejemplo: <a href="amigobro@gmail.com">amigobro@gmail.com</a>""",
    "request_amount": """Introduzca el importe que desea retirar.

El importe mínimo de retirada es <b>75.000 Pesos</b>

💵 Su saldo %<b>CURRENCIA</b>% <b>{balance} Pesos</b>""",
    "request_amount_wrong_value": """❌  No hay fondos suficientes en su saldo. El importe mínimo de retirada es <b>75.000 Pesos</b>

💵 Su saldo %<b>CURRENCIA</b>% <b>{balance} Pesos</b>""",
    "request_created": """Con éxito ✅ 
Su solicitud ha sido enviada ✅ 
Espere 48 horas para una respuesta""",
    "referr_notification": """🎉 Alguien se registró en el bot usando su enlace 🎉

<b>+ {amount:.1f} Pesos</b> 💰 

📢 Has invitado a: <b>{referrals} usuarios</b>
📣 Tus amigos han invitado a: <b>{rereferrals} usuarios</b>
💸 Su saldo: <b>{balance} Pesos</b>""",
    "rereferr_notification": """🎉 Alguien se registró en el bot utilizando el enlace de tu amigo 🎉

<b>+ {amount:.1f} Pesos</b> 💰 

📢 Has invitado a: <b>{referrals} usuarios</b>
📣 Tus amigos han invitado a: <b>{rereferrals} usuarios</b>
💸 Su saldo: <b>{balance} Pesos</b>""",
    "ad_msg_withdraw": """Para enviar una solicitud de retirada, debe estar suscrito al canal de nuestro patrocinador. 

Este chico es un joven millonario de Chile , a los 36 años tuvo un éxito increíble en su trabajo y ahora ayuda a la gente a ganar dinero por internet y comparte esta información en su canal


Suscríbase a su canal ahora mismo, vea de 5 a 10 publicaciones y haga clic para confirmar su suscripción✅"""

}