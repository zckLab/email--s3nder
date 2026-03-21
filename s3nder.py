import smtplib
import os
import random
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Tuple, Optional

# Ensure paths are relative to this script, not the working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Try to load dotenv, ignore if not found (standard library fallback)
try:
    from dotenv import load_dotenv # type: ignore
    load_dotenv(os.path.join(SCRIPT_DIR, 'example.env'))
except ImportError:
    pass

def manual_load_env(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

if 'EMAIL_USER' not in os.environ:
    manual_load_env(os.path.join(SCRIPT_DIR, 'example.env'))

UI_DICT = {
    "en": {"num_prompt": "How many companies do you want to email? ", "invalid_num": "Invalid number.", "company_header": "\n--- Company {i} of {total} ---", "email_prompt": "Company Email: ", "invalid_email": "Invalid email format.", "name_c_prompt": "Company Name: ", "city_prompt": "City: ", "service_prompt": "Their Industry/Service: ", "rating_prompt": "Rating (e.g., 4.8): ", "invalid_rating": "Invalid rating format.", "reviews_prompt": "Number of Reviews: ", "value_hook": "Your Service/Offer (e.g. 'AI automation'): ", "custom_sub": "\nCustom Subject: ", "custom_body": "Custom Body (Type 'END' on a new line to finish):", "start_header": "STARTING EMAIL SENDING PROCESS", "lang_label": "Language: {lang} | Companies: {count}", "err_template": "  ⚠️ ERROR: Could not generate template for {name}", "preview_sub": "Subject: ", "send_confirm": "  Send to {email}? (y/n): ", "skipped": "  ⏩ SKIPPED", "sending": "  Sending email...", "sent": "  ✅ SENT!", "failed": "  ❌ FAILED!", "completed": "COMPLETED! Sent: {sent} | Failed: {failed}"},
    "pt": {"num_prompt": "Quantas empresas você quer contatar? ", "invalid_num": "Número inválido.", "company_header": "\n--- Empresa {i} de {total} ---", "email_prompt": "E-mail da Empresa: ", "invalid_email": "Formato de e-mail inválido.", "name_c_prompt": "Nome da Empresa: ", "city_prompt": "Cidade: ", "service_prompt": "Nicho/Serviço Deles: ", "rating_prompt": "Avaliação (ex: 4.8): ", "invalid_rating": "Formato de avaliação inválido.", "reviews_prompt": "Número de Avaliações: ", "value_hook": "Seu Serviço/Oferta (ex: 'automação'): ", "custom_sub": "\nAssunto Personalizado: ", "custom_body": "Corpo do E-mail (Digite 'END' em uma nova linha para finalizar):", "start_header": "INICIANDO PROCESSO DE ENVIO", "lang_label": "Idioma: {lang} | Empresas: {count}", "err_template": "  ⚠️ ERRO: Não foi possível gerar template para {name}", "preview_sub": "Assunto: ", "send_confirm": "  Enviar para {email}? (y/n): ", "skipped": "  ⏩ IGNORADO", "sending": "  Enviando e-mail...", "sent": "  ✅ ENVIADO!", "failed": "  ❌ FALHOU!", "completed": "CONCLUÍDO! Enviados: {sent} | Falharam: {failed}"},
    "es": {"num_prompt": "¿A cuántas empresas quieres enviar correos? ", "invalid_num": "Número inválido.", "company_header": "\n--- Empresa {i} de {total} ---", "email_prompt": "Correo de la Empresa: ", "invalid_email": "Formato de correo inválido.", "name_c_prompt": "Nombre de la Empresa: ", "city_prompt": "Ciudad: ", "service_prompt": "Industria/Servicio de Ellos: ", "rating_prompt": "Calificación (ej: 4.8): ", "invalid_rating": "Formato de calificación inválido.", "reviews_prompt": "Número de Reseñas: ", "value_hook": "Tu Servicio/Oferta (ej: 'SEO'): ", "custom_sub": "\nAsunto Personalizado: ", "custom_body": "Cuerpo del Correo (Escribe 'END' en una nueva línea al terminar):", "start_header": "INICIANDO PROCESSO DE ENVÍO", "lang_label": "Idioma: {lang} | Empresas: {count}", "err_template": "  ⚠️ ERROR: No se pudo generar plantilla para {name}", "preview_sub": "Asunto: ", "send_confirm": "  ¿Enviar a {email}? (y/n): ", "skipped": "  ⏩ OMITIDO", "sending": "  Enviando correo...", "sent": "  ✅ ¡ENVIADO!", "failed": "  ❌ ¡FALLÓ!", "completed": "¡COMPLETADO! Enviados: {sent} | Fallidos: {failed}"},
    "fr": {"num_prompt": "Combien d'entreprises souhaitez-vous contacter ? ", "invalid_num": "Numéro invalide.", "company_header": "\n--- Entreprise {i} sur {total} ---", "email_prompt": "Email de l'Entreprise : ", "invalid_email": "Format d'email invalide.", "name_c_prompt": "Nom de l'Entreprise : ", "city_prompt": "Ville : ", "service_prompt": "Leur Industrie/Service : ", "rating_prompt": "Note (ex: 4.8) : ", "invalid_rating": "Format de note invalide.", "reviews_prompt": "Nombre d'avis : ", "value_hook": "Votre Service/Offre (ex: 'SEO') : ", "custom_sub": "\nSujet Personnalisé : ", "custom_body": "Corps du message (Tapez 'END' sur une nouvelle ligne pour terminer) :", "start_header": "DÉMARRAGE DU PROCESSUS D'ENVOI", "lang_label": "Langue : {lang} | Entreprises : {count}", "err_template": "  ⚠️ ERREUR : Impossible de générer le modèle pour {name}", "preview_sub": "Sujet : ", "send_confirm": "  Envoyer à {email} ? (y/n) : ", "skipped": "  ⏩ IGNORÉ", "sending": "  Envoi de l'email...", "sent": "  ✅ ENVOYÉ !", "failed": "  ❌ ÉCHEC !", "completed": "TERMINÉ ! Envoyés : {sent} | Échecs : {failed}"},
    "de": {"num_prompt": "Wie viele Unternehmen möchten Sie kontaktieren? ", "invalid_num": "Ungültige Zahl.", "company_header": "\n--- Unternehmen {i} von {total} ---", "email_prompt": "Unternehmens-E-Mail: ", "invalid_email": "Ungültiges E-Mail-Format.", "name_c_prompt": "Unternehmensname: ", "city_prompt": "Stadt: ", "service_prompt": "Deren Branche/Service: ", "rating_prompt": "Bewertung (z.B. 4.8): ", "invalid_rating": "Ungültiges Bewertungsformat.", "reviews_prompt": "Anzahl der Rezensionen: ", "value_hook": "Ihr Service/Angebot (z.B. 'SEO'): ", "custom_sub": "\nBenutzerdefinierter Betreff: ", "custom_body": "Nachrichtentext (Tippen Sie 'END' in eine neue Zeile zum Beenden):", "start_header": "START DES E-MAIL-VERSANDPROZESSES", "lang_label": "Sprache: {lang} | Unternehmen: {count}", "err_template": "  ⚠️ FEHLER: Vorlage für {name} konnte nicht erstellt werden", "preview_sub": "Betreff: ", "send_confirm": "  An {email} senden? (y/n): ", "skipped": "  ⏩ ÜBERSPRUNGEN", "sending": "  E-Mail wird gesendet...", "sent": "  ✅ GESENDET!", "failed": "  ❌ FEHLGESCHLAGEN!", "completed": "ABGESCHLOSSEN! Gesendet: {sent} | Fehlgeschlagen: {failed}"},
    "it": {"num_prompt": "A quante aziende vuoi inviare email? ", "invalid_num": "Numero non valido.", "company_header": "\n--- Azienda {i} di {total} ---", "email_prompt": "Email Aziendale: ", "invalid_email": "Formato email non valido.", "name_c_prompt": "Nome Azienda: ", "city_prompt": "Città: ", "service_prompt": "Il loro Settore/Servizio: ", "rating_prompt": "Valutazione (es. 4.8): ", "invalid_rating": "Formato valutazione non valido.", "reviews_prompt": "Numero di Recensioni: ", "value_hook": "Il tuo Servizio/Offerta (es. 'SEO'): ", "custom_sub": "\nOggetto Personalizzato: ", "custom_body": "Corpo del messaggio (Digita 'END' in una nuova riga per finire):", "start_header": "AVVIO DEL PROCESSO DI INVIO", "lang_label": "Lingua: {lang} | Aziende: {count}", "err_template": "  ⚠️ ERRORE: Impossibile generare il modello per {name}", "preview_sub": "Oggetto: ", "send_confirm": "  Inviare a {email}? (y/n): ", "skipped": "  ⏩ IGNORATO", "sending": "  Invio email in corso...", "sent": "  ✅ INVIATO!", "failed": "  ❌ FALLITO!", "completed": "COMPLETATO! Inviati: {sent} | Falliti: {failed}"},
    "nl": {"num_prompt": "Hoeveel bedrijven wilt u e-mailen? ", "invalid_num": "Ongeldig nummer.", "company_header": "\n--- Bedrijf {i} van {total} ---", "email_prompt": "Bedrijfs-e-mail: ", "invalid_email": "Ongeldig e-mailformaat.", "name_c_prompt": "Bedrijfsnaam: ", "city_prompt": "Stad: ", "service_prompt": "Hun Branche/Service: ", "rating_prompt": "Beoordeling (bijv. 4.8): ", "invalid_rating": "Ongeldig beoordelingsformaat.", "reviews_prompt": "Aantal Recensies: ", "value_hook": "Uw Service/Aanbod (bijv. 'SEO'): ", "custom_sub": "\nAangepast Onderwerp: ", "custom_body": "E-mailtekst (Typ 'END' op een nieuwe regel om af te sluiten):", "start_header": "E-MAIL VERZENDPROCES STARTEN", "lang_label": "Taal: {lang} | Bedrijven: {count}", "err_template": "  ⚠️ FOUT: Kon geen sjabloon genereren voor {name}", "preview_sub": "Onderwerp: ", "send_confirm": "  Verzenden naar {email}? (y/n): ", "skipped": "  ⏩ OVERGESLAGEN", "sending": "  E-mail verzenden...", "sent": "  ✅ VERZONDEN!", "failed": "  ❌ MISLUKT!", "completed": "VOLTOOID! Verzonden: {sent} | Mislukt: {failed}"},
    "pl": {"num_prompt": "Do ilu firm chcesz wysłać e-mail? ", "invalid_num": "Nieprawidłowa liczba.", "company_header": "\n--- Firma {i} z {total} ---", "email_prompt": "E-mail Firmowy: ", "invalid_email": "Nieprawidłowy format e-mail.", "name_c_prompt": "Nazwa Firmy: ", "city_prompt": "Miasto: ", "service_prompt": "Ich Branża/Usługa: ", "rating_prompt": "Ocena (np. 4.8): ", "invalid_rating": "Nieprawidłowy format oceny.", "reviews_prompt": "Liczba Opinii: ", "value_hook": "Twoja Usługa/Oferta (np. 'SEO'): ", "custom_sub": "\nNiestandardowy Temat: ", "custom_body": "Treść e-maila (Wpisz 'END' w nowej linii, aby zakończyć):", "start_header": "ROZPOCZYNANIE PROCESU WYSYŁANIA", "lang_label": "Język: {lang} | Firmy: {count}", "err_template": "  ⚠️ BŁĄD: Nie można wygenerować szablonu dla {name}", "preview_sub": "Temat: ", "send_confirm": "  Wysłać do {email}? (y/n): ", "skipped": "  ⏩ POMINIĘTO", "sending": "  Wysyłanie e-maila...", "sent": "  ✅ WYSŁANO!", "failed": "  ❌ NIE POWIODŁO SIĘ!", "completed": "ZAKOŃCZONO! Wysłano: {sent} | Nie udane: {failed}"},
    "ru": {"num_prompt": "Skol'kim kompaniyam vy hotite otpravit' email? ", "invalid_num": "Nevernoe chislo.", "company_header": "\n--- Kompaniya {i} iz {total} ---", "email_prompt": "Email kompanii: ", "invalid_email": "Nevernyy format email.", "name_c_prompt": "Nazvanie kompanii: ", "city_prompt": "Gorod: ", "service_prompt": "Ikh otrasl'/usluga: ", "rating_prompt": "Reyting (napr. 4.8): ", "invalid_rating": "Nevernyy format reytinga.", "reviews_prompt": "Kolichestvo otzyvov: ", "value_hook": "Vasha usluga (napr. 'SEO'): ", "custom_sub": "\nSvoy zagolovok: ", "custom_body": "Tekst pis'ma (Vvedite 'END' s novoy stroki dlya zaversheniya):", "start_header": "NACHALO OTPRAVKI PIS'EM", "lang_label": "Yazyk: {lang} | Kompanii: {count}", "err_template": "  ⚠️ OSHIBKA: Ne udalos' sozdat' shablon dlya {name}", "preview_sub": "Tema: ", "send_confirm": "  Otpravit' na {email}? (y/n): ", "skipped": "  ⏩ PROPUSHCHENO", "sending": "  Otpravka pis'ma...", "sent": "  ✅ OTPRAVLENO!", "failed": "  ❌ OSHIBKA!", "completed": "ZAVERSHENO! Otpravleno: {sent} | Oshibki: {failed}"},
    "sv": {"num_prompt": "Hur många företag vill du maila? ", "invalid_num": "Ogiltigt nummer.", "company_header": "\n--- Företag {i} av {total} ---", "email_prompt": "Företagets E-post: ", "invalid_email": "Ogiltigt format på e-post.", "name_c_prompt": "Företagsnamn: ", "city_prompt": "Stad: ", "service_prompt": "Deras Bransch/Tjänst: ", "rating_prompt": "Betyg (t.ex. 4.8): ", "invalid_rating": "Ogiltigt betygsformat.", "reviews_prompt": "Antal Recensioner: ", "value_hook": "Din Tjänst/Erbjudande (t.ex. 'SEO'): ", "custom_sub": "\nAnpassat Ämne: ", "custom_body": "Meddelandetext (Skriv 'END' på en ny rad för att avsluta):", "start_header": "STARTAR E-POSTUTSKICK", "lang_label": "Språk: {lang} | Företag: {count}", "err_template": "  ⚠️ FEL: Kunde inte generera mall för {name}", "preview_sub": "Ämne: ", "send_confirm": "  Skicka till {email}? (y/n): ", "skipped": "  ⏩ HOPPADE ÖVER", "sending": "  Skickar e-post...", "sent": "  ✅ SKICKAT!", "failed": "  ❌ MISSLYCKADES!", "completed": "KLART! Skickade: {sent} | Misslyckade: {failed}"},
    "no": {"num_prompt": "Hvor mange selskaper vil du sende e-post til? ", "invalid_num": "Ugyldig nummer.", "company_header": "\n--- Selskap {i} av {total} ---", "email_prompt": "Firma E-post: ", "invalid_email": "Ugyldig e-postformat.", "name_c_prompt": "Firmanavn: ", "city_prompt": "By: ", "service_prompt": "Deres Bransje/Tjeneste: ", "rating_prompt": "Vurdering (f.eks. 4.8): ", "invalid_rating": "Ugyldig vurderingsformat.", "reviews_prompt": "Antall Anmeldelser: ", "value_hook": "Din Tjeneste/Tilbud (f.eks. 'SEO'): ", "custom_sub": "\nEgendefinert Emne: ", "custom_body": "Meldingstekst (Skriv 'END' på en ny linje for å avslutte):", "start_header": "STARTER UTSENDING AV E-POST", "lang_label": "Språk: {lang} | Selskaper: {count}", "err_template": "  ⚠️ FEIL: Kunne ikke generere mal for {name}", "preview_sub": "Emne: ", "send_confirm": "  Send til {email}? (y/n): ", "skipped": "  ⏩ HOPPET OVER", "sending": "  Sender e-post...", "sent": "  ✅ SENDT!", "failed": "  ❌ MISLYKTES!", "completed": "FULLFØRT! Sendte: {sent} | Mislyktes: {failed}"},
    "da": {"num_prompt": "Hvor mange virksomheder vil du maile til? ", "invalid_num": "Ugyldigt nummer.", "company_header": "\n--- Virksomhed {i} af {total} ---", "email_prompt": "Firma E-mail: ", "invalid_email": "Ugyldigt e-mailformat.", "name_c_prompt": "Firmanavn: ", "city_prompt": "By: ", "service_prompt": "Deres Branche/Tjeneste: ", "rating_prompt": "Bedømmelse (f.eks. 4.8): ", "invalid_rating": "Ugyldigt bedømmelsesformat.", "reviews_prompt": "Antal Anmeldelser: ", "value_hook": "Din Tjeneste/Tilbud (f.eks. 'SEO'): ", "custom_sub": "\nBrugerdefineret Emne: ", "custom_body": "Beskedtekst (Skriv 'END' på en ny linje for at afslutte):", "start_header": "STARTER E-MAIL UDSENDELSE", "lang_label": "Sprog: {lang} | Virksomheder: {count}", "err_template": "  ⚠️ FEJL: Kunne ikke generere skabelon for {name}", "preview_sub": "Emne: ", "send_confirm": "  Send til {email}? (y/n): ", "skipped": "  ⏩ SPRUNGET OVER", "sending": "  Sender e-mail...", "sent": "  ✅ SENDT!", "failed": "  ❌ FEJLEDE!", "completed": "AFSLUTTET! Sendte: {sent} | Fejlede: {failed}"},
    "fi": {"num_prompt": "Kuinka monelle yritykselle haluat lähettää sähköpostia? ", "invalid_num": "Virheellinen numero.", "company_header": "\n--- Yritys {i} / {total} ---", "email_prompt": "Yrityksen Sähköposti: ", "invalid_email": "Virheellinen sähköpostimuoto.", "name_c_prompt": "Yrityksen Nimi: ", "city_prompt": "Kaupunki: ", "service_prompt": "Heidän Toimialansa/Palvelu: ", "rating_prompt": "Arvio (esim. 4.8): ", "invalid_rating": "Virheellinen arvion muoto.", "reviews_prompt": "Arvostelujen määrä: ", "value_hook": "Sinun Palvelusi/Tarjouksesi (esim. 'SEO'): ", "custom_sub": "\nMukautettu Aihe: ", "custom_body": "Viestin teksti (Kirjoita 'END' uudelle riville lopettaaksesi):", "start_header": "SÄHKÖPOSTIEN LÄHETYS ALKAA", "lang_label": "Kieli: {lang} | Yritykset: {count}", "err_template": "  ⚠️ VIRHE: Ei voitu luoda mallia yritykselle {name}", "preview_sub": "Aihe: ", "send_confirm": "  Lähetä osoitteeseen {email}? (y/n): ", "skipped": "  ⏩ OHITETTU", "sending": "  Lähetetään sähköpostia...", "sent": "  ✅ LÄHETETTY!", "failed": "  ❌ EPÄONNISTUI!", "completed": "VALMIS! Lähetetty: {sent} | Epäonnistui: {failed}"},
    "tr": {"num_prompt": "Kaç şirkete e-posta göndermek istiyorsunuz? ", "invalid_num": "Geçersiz sayı.", "company_header": "\n--- Şirket {i} / {total} ---", "email_prompt": "Şirket E-postası: ", "invalid_email": "Geçersiz e-posta formatı.", "name_c_prompt": "Şirket Adı: ", "city_prompt": "Şehir: ", "service_prompt": "Sektörleri/Hizmetleri: ", "rating_prompt": "Derecelendirme (örn. 4.8): ", "invalid_rating": "Geçersiz derecelendirme formatı.", "reviews_prompt": "Yorum Sayısı: ", "value_hook": "Sizin Hizmetiniz/Teklifiniz (örn. 'SEO'): ", "custom_sub": "\nÖzel Konu: ", "custom_body": "E-posta Gövdesi (Bitirmek için yeni bir satıra 'END' yazın):", "start_header": "E-POSTA GÖNDERİM SÜRECİ BAŞLIYOR", "lang_label": "Dil: {lang} | Şirketler: {count}", "err_template": "  ⚠️ HATA: {name} için şablon oluşturulamadı", "preview_sub": "Konu: ", "send_confirm": "  {email} adresine gönderilsin mi? (y/n): ", "skipped": "  ⏩ ATLANDI", "sending": "  E-posta gönderiliyor...", "sent": "  ✅ GÖNDERİLDİ!", "failed": "  ❌ BAŞARISIZ!", "completed": "TAMAMLANDI! Gönderilen: {sent} | Başarısız: {failed}"},
    "zh": {"num_prompt": "你想发送电子邮件给多少家公司？ ", "invalid_num": "无效数字。", "company_header": "\n--- 公司 {i} / {total} ---", "email_prompt": "公司电邮: ", "invalid_email": "无效的电邮格式。", "name_c_prompt": "公司名称: ", "city_prompt": "城市: ", "service_prompt": "他们的行业/服务: ", "rating_prompt": "评分 (例如， 4.8): ", "invalid_rating": "无效的评分格式。", "reviews_prompt": "评论数量: ", "value_hook": "您的服务/报价 (例如 'SEO'): ", "custom_sub": "\n自定义主题: ", "custom_body": "电邮正文 (在新一行输入 'END' 来完成):", "start_header": "开始发送电子邮件", "lang_label": "语言: {lang} | 公司: {count}", "err_template": "  ⚠️ 错误: 无法生成 {name} 的模板", "preview_sub": "主题: ", "send_confirm": "  发送至 {email}? (y/n): ", "skipped": "  ⏩ 已跳过", "sending": "  正在发送电子邮件...", "sent": "  ✅ 已发送!", "failed": "  ❌ 发送失败!", "completed": "完成！已发送: {sent} | 失败: {failed}"},
    "ja": {"num_prompt": "何社にメールを送信しますか？ ", "invalid_num": "無効な数字です。", "company_header": "\n--- 会社 {i} / {total} ---", "email_prompt": "会社のメールアドレス: ", "invalid_email": "無効なメール形式。", "name_c_prompt": "会社名: ", "city_prompt": "都市: ", "service_prompt": "彼らの業界/サービス: ", "rating_prompt": "評価 (例： 4.8): ", "invalid_rating": "無効な評価形式。", "reviews_prompt": "レビュー数: ", "value_hook": "あなたのサービス/提案 (例 'SEO'): ", "custom_sub": "\nカスタム件名: ", "custom_body": "メール本文 (新しい行に 'END' と入力して終了します):", "start_header": "メール送信プロセスを開始します", "lang_label": "言語: {lang} | 会社: {count}", "err_template": "  ⚠️ エラー: {name} のテンプレートを生成できませんでした", "preview_sub": "件名: ", "send_confirm": "  {email} に送信しますか？ (y/n): ", "skipped": "  ⏩ スキップしました", "sending": "  メールを送信中...", "sent": "  ✅ 送信完了!", "failed": "  ❌ 失敗!", "completed": "完了！ 送信済み: {sent} | 失敗: {failed}"},
    "ko": {"num_prompt": "몇 개의 회사에 이메일을 보내시겠습니까? ", "invalid_num": "유효하지 않은 숫자입니다.", "company_header": "\n--- 회사 {i} / {total} ---", "email_prompt": "회사 이메일: ", "invalid_email": "유효하지 않은 이메일 형식입니다.", "name_c_prompt": "회사 이름: ", "city_prompt": "도시: ", "service_prompt": "그들의 산업/서비스: ", "rating_prompt": "평점 (예: 4.8): ", "invalid_rating": "유효하지 않은 평점 형식입니다.", "reviews_prompt": "리뷰 수: ", "value_hook": "당신의 서비스/제공 (예: 'SEO'): ", "custom_sub": "\n사용자 정의 제목: ", "custom_body": "이메일 본문 (새 줄에 'END'를 입력하여 마침):", "start_header": "이메일 전송 프로세스 시작", "lang_label": "언어: {lang} | 회사: {count}", "err_template": "  ⚠️ 오류: {name}에 대한 템플릿을 생성할 수 없습니다", "preview_sub": "제목: ", "send_confirm": "  {email}로 보내시겠습니까? (y/n): ", "skipped": "  ⏩ 건너뜀", "sending": "  이메일 전송 중...", "sent": "  ✅ 전송 완료!", "failed": "  ❌ 실패!", "completed": "완료! 전송됨: {sent} | 실패: {failed}"},
    "ar": {"num_prompt": "كم عدد الشركات التي تريد مراسلتها؟ ", "invalid_num": "رقم غير صالح.", "company_header": "\n--- شركة {i} من {total} ---", "email_prompt": "بريد الشركة الإلكتروني: ", "invalid_email": "تنسيق بريد إلكتروني غير صالح.", "name_c_prompt": "اسم الشركة: ", "city_prompt": "المدينة: ", "service_prompt": "صناعتهم / خدمتهم: ", "rating_prompt": "التقييم (مثل: 4.8): ", "invalid_rating": "تنسيق تقييم غير صالح.", "reviews_prompt": "عدد المراجعات: ", "value_hook": "خدمتك / عرضك (مثل: 'SEO'): ", "custom_sub": "\nموضوع مخصص: ", "custom_body": "نص البريد الإلكتروني (اكتب 'END' في سطر جديد للإنهاء):", "start_header": "بدء عملية إرسال البريد الإلكتروني", "lang_label": "اللغة: {lang} | الشركات: {count}", "err_template": "  ⚠️ خطأ: لم يتمكن من إنشاء قالب لـ {name}", "preview_sub": "الموضوع: ", "send_confirm": "  إرسال إلى {email}؟ (y/n): ", "skipped": "  ⏩ تم التخطي", "sending": "  إرسال البريد الإلكتروني...", "sent": "  ✅ تم الإرسال!", "failed": "  ❌ فشل!", "completed": "مكتمل! تم الإرسال: {sent} | الفشل: {failed}"},
    "hi": {"num_prompt": "Aap kitni companiyon ko email bhejna chahte hain? ", "invalid_num": "Amaanya sankhya.", "company_header": "\n--- Company {i} of {total} ---", "email_prompt": "Company Email: ", "invalid_email": "Amaanya email format.", "name_c_prompt": "Company Ka Naam: ", "city_prompt": "Shahar: ", "service_prompt": "Unka Udyog/Seva: ", "rating_prompt": "Rating (Jaise: 4.8): ", "invalid_rating": "Amaanya rating format.", "reviews_prompt": "Reviews Ki Sankhya: ", "value_hook": "Aapki Seva/Peshkash (Jaise: 'SEO'): ", "custom_sub": "\nCustom Vishay: ", "custom_body": "Email Body (Pura karne ke liye nayi line me 'END' type karein):", "start_header": "EMAIL BHEJNE KI PRAKRIYA SHURU", "lang_label": "Bhasha: {lang} | Companies: {count}", "err_template": "  ⚠️ TRUTI: {name} ke liye template nahi ban saka", "preview_sub": "Vishay: ", "send_confirm": "  Kya {email} ko bhejein? (y/n): ", "skipped": "  ⏩ CHHOD DIYA", "sending": "  Email bhej raha hai...", "sent": "  ✅ BHEJA GAYA!", "failed": "  ❌ VIFAL!", "completed": "PURA HUA! Bheje gaye: {sent} | Vifal: {failed}"}
}
def loc(key, base_lang="en", **kwargs):
    l = base_lang if base_lang in UI_DICT else "en"
    text = UI_DICT.get(l, UI_DICT["en"]).get(key, UI_DICT["en"][key])
    return text.format(**kwargs) if kwargs else text

def get_base_languages():
    bases = set()
    lang_dir = os.path.join(SCRIPT_DIR, "languages")
    if os.path.exists(lang_dir):
        for f in os.listdir(lang_dir):
            if f.startswith("PROMPTemail_") and f.endswith(".md"):
                name = f.replace("PROMPTemail_", "").replace(".md", "")
                base = name.split("_")[0]
                bases.add(base)
    return sorted(list(bases))

def get_templates_for_lang(lang: str):
    templates = []
    lang_dir = os.path.join(SCRIPT_DIR, "languages")
    if os.path.exists(lang_dir):
        for f in os.listdir(lang_dir):
            if f.startswith(f"PROMPTemail_{lang}") and f.endswith(".md"):
                if f == f"PROMPTemail_{lang}.md" or f.startswith(f"PROMPTemail_{lang}_"):
                    templates.append(os.path.join(lang_dir, f))
    return templates

def parse_spintax(text: str) -> str:
    def replace_spin(match):
        options = match.group(1).split("|")
        return random.choice(options)
    while re.search(r"\{([^{}]*\|[^{}]*)\}", text):
        text = re.sub(r"\{([^{}]*\|[^{}]*)\}", replace_spin, text)
    return text

def validate_email(email: str) -> bool:
    return "@" in email

def validate_rating(rating: str) -> bool:
    if not rating: return True
    return bool(re.match(r"^[0-5](\.\d)?$", rating))

def process_text_replacements(subject: str, body: str, placeholders: dict) -> Tuple[str, str]:
    for key, value in placeholders.items():
        subject = subject.replace(key, value)
        body = body.replace(key, value)
    subject = parse_spintax(subject)
    body = parse_spintax(body)
    return subject, body

def get_template_text(filepath: str) -> Tuple[Optional[str], Optional[str]]:
    if not os.path.exists(filepath):
        return None, None
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        return None, None
        
    subject = "Subject"
    if ":" in lines[0] or "：" in lines[0]:
        sep = ":" if ":" in lines[0] else "："
        subject = lines[0].split(sep, 1)[1].strip()
        body = "".join(l for idx, l in enumerate(lines) if idx > 0).strip()
    else:
        body = "".join(lines).strip()
    return subject, body

def send_email(to_email: str, subject: str, body: str) -> bool:
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    if not sender_email or not sender_password:
        return False

    msg = MIMEMultipart()
    msg["From"] = str(sender_email)
    msg["To"] = to_email
    msg["Subject"] = str(subject)
    msg.attach(MIMEText(str(body), "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(str(sender_email), str(sender_password))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

def main():
    splash = r"""
                            .
                          A       ;
                |   ,--,-/ \---,-/|  ,
               _|\,'. /|      /|   `/|-.
           \`.'    /|      ,            `;.
          ,'\   A     A         A   A _ /| `.;
        ,/  _              A       _  / _   /|  ;
       /\  / \   ,  ,           A  /    /     `/|
      /_| | _ \         ,     ,             ,/  \
     // | |/ `.\  ,-      ,       ,   ,/ ,/      \/
     / @| |@  / /'   \  \      ,              >  /|    ,--.
    |\_/   \_/ /      |  |           ,  ,/        \  ./' __:..
    |  __ __  |       |  | .--.  ,         >  >   |-'   /     `
  ,/| /  '  \ |       |  |     \      ,           |    /
 /  |<--.__,->|       |  | .    `.        >  >    /   (
/_,' \\  ^  /  \     /  /   `.    >--            /^\   |
      \\___/    \   /  /      \__'     \   \   \/   \  |
       `.   |/          ,  ,                  /`\    \  )
         \  '  |/    ,       V    \          /        `-\
          `|/  '  V      V           \    \.'            \_
           '`-.       V       V        \./'\
               `|/-.      \ /   \ /,---`\         Z.KLIRT
                /   `._____V_____V'
                           '     '
    """
    print(splash)
    print("--- S3NDER ---")
    
    print("\n--- Your Credentials ---")
    sender_name = input("Your Name: ").strip()
    sender_occupation = input("Your Occupation/Role: ").strip()
    sender_portfolio = input("Your Portfolio/Website: ").strip()

    available_bases = get_base_languages()
    
    while True:
        print("\nType 'custom' to write your own email locally in the terminal.")
        lang_input = input("Select Language (e.g. pt, en, es) (or 'help' for list): ").strip()
        
        if lang_input == "help":
            print("\nAvailable Languages:")
            for i in range(0, len(available_bases), 5):
                row = []
                for k, base in enumerate(available_bases):
                    if i <= k < i + 5:
                        row.append(base)
                print("  " + "    ".join(f"{t:<5}" for t in row))
            continue
            
        if lang_input == "custom" or lang_input in available_bases:
            selected_lang = lang_input
            break
        print(f"Error: '{lang_input}' is not recognized.")

    base_lang = "en"
    if selected_lang != "custom":
        if selected_lang != "en" and selected_lang in UI_DICT:
            change_ui = input(f"Switch terminal language to {selected_lang}? (y/N): ").strip().lower()
            if change_ui == 'y':
                base_lang = selected_lang
                
    custom_subject_tmpl = ""
    custom_body_tmpl = ""
    pool_templates = []
    
    if selected_lang == "custom":
        print("\n--- Custom Template Mode ---")
        print("You can use variables like {{company_name}}, {{city}}, {{Value_Hook}}, etc.")
        custom_subject_tmpl = input(loc("custom_sub", base_lang))
        print(loc("custom_body", base_lang))
        lines: list = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        custom_body_tmpl = "\n".join(lines)
    else:
        pool_templates = get_templates_for_lang(selected_lang)

    while True:
        try:
            num_emails = int(input("\n" + loc("num_prompt", base_lang)).strip())
            break
        except ValueError:
            print(loc("invalid_num", base_lang))

    companies = []
    for i in range(num_emails):
        print(loc("company_header", base_lang, i=i+1, total=num_emails))
        
        while True:
            company_email = input(loc("email_prompt", base_lang)).strip()
            if validate_email(company_email): break
            print(loc("invalid_email", base_lang))

        company_name = input(loc("name_c_prompt", base_lang)).strip().title()
        city = input(loc("city_prompt", base_lang)).strip().title()
        service_type = input(loc("service_prompt", base_lang)).strip().title()
        
        while True:
            rating = input(loc("rating_prompt", base_lang)).strip()
            if validate_rating(rating): break
            print(loc("invalid_rating", base_lang))

        reviews = input(loc("reviews_prompt", base_lang)).strip()
        value_hook = input(loc("value_hook", base_lang)).strip()
        
        companies.append({
            "email": company_email,
            "name": company_name,
            "city": city,
            "service_type": service_type,
            "rating": rating,
            "reviews": reviews,
            "value_hook": value_hook
        })

    print("\n" + "="*40)
    print(loc("start_header", base_lang))
    print(loc("lang_label", base_lang, lang=str(selected_lang).upper(), count=len(companies)))
    if selected_lang != "custom":
        print(f"Template Pool Size: {len(pool_templates)} variation(s) for random selection.")
    print("="*40)
    
    counts = {"sent": 0, "failed": 0}
    
    for i, company in enumerate(companies):
        print(f"\n[{i+1}/{len(companies)}] {company['name']} -> {company['email']}")
        
        if selected_lang == "custom":
            raw_sub = custom_subject_tmpl
            raw_body = custom_body_tmpl
        else:
            if not pool_templates:
                print(loc("err_template", base_lang, name=company['name']))
                counts["failed"] += 1
                continue
                
            chosen_file = random.choice(pool_templates)
            raw_sub, raw_body = get_template_text(chosen_file)
            
        if not raw_sub or not raw_body:
            print(loc("err_template", base_lang, name=company['name']))
            counts["failed"] += 1
            continue
            
        raw_sub = str(raw_sub)
        raw_body = str(raw_body)

        placeholders = {
            "{{company_name}}": company["name"],
            "{{city}}": company["city"],
            "{{service_type}}": company["service_type"],
            "{{rating}}": company["rating"],
            "{{reviews}}": company["reviews"],
            "{{Value_Hook}}": company["value_hook"],
            "{Name}": sender_name,
            "{Occupation}": sender_occupation,
            "{WebSite/Portfolio}": sender_portfolio
        }
        
        subject, body = process_text_replacements(raw_sub, raw_body, placeholders)
        
        subject = str(subject)
        body = str(body)
        
        print("\n  " + loc("preview_sub", base_lang) + subject)
        print("  " + "-" * 30)
        preview = body[:300]  # type: ignore
        print("  " + preview.replace("\n", "\n  ") + "...")
        print("  " + "-" * 30)
        
        confirm = input("\n" + loc("send_confirm", base_lang, email=company['email'])).lower().strip()
        if confirm != 'y':
            print(loc("skipped", base_lang))
            continue
        
        print(loc("sending", base_lang))
        if send_email(company["email"], subject, body):
            print(loc("sent", base_lang))
            counts["sent"] += 1
        else:
            print(loc("failed", base_lang))
            counts["failed"] += 1
    
    print("\n" + "="*40)
    print(loc("completed", base_lang, sent=counts["sent"], failed=counts["failed"]))
    print("="*40)

if __name__ == "__main__":
    main()
