
import math
from itertools import combinations
from datetime import datetime
from html import escape
from typing import Any, Mapping, Sequence, TypeAlias

import numpy as np
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Decision Framework Wizard",
    page_icon="DF",
    layout="wide",
    initial_sidebar_state="expanded",
)


DOMAINS = [
    {
        "key": 'economic_quality',
        "label": 'Фінанси',
        "short": 'Ф',
        "explain": 'Важливість дохідності, якості cash flow, ліквідності та захисту капіталу на найближчі 12–24 місяці.',
        "question": 'Якщо доведеться обирати, наскільки я зараз захищаю фінансовий результат і капітал?',
    },
    {
        "key": 'strategic_significance',
        "label": 'Стратегія',
        "short": 'С',
        "explain": 'Важливість майбутніх можливостей, навичок, систем і довгострокового посилення власної позиції.',
        "question": 'Наскільки я зараз готовий ставити майбутнє посилення вище короткострокової вигоди?',
    },
    {
        "key": 'asset_controllability',
        "label": 'Керованість',
        "short": 'К',
        "explain": 'Важливість впливу на результат, якості людей, прозорості правил, цифр і захисту інтересів.',
        "question": 'Наскільки для мене зараз критично мати контроль, ясність і вплив?',
    },
    {
        "key": 'management_load',
        "label": 'Навантаження',
        "short": 'Н',
        "explain": 'Важливість збереження часу, уваги, фокусу та захисту від постійного перемикання.',
        "question": 'Наскільки я зараз захищаю свій час і операційний фокус?',
    },
    {
        "key": 'personal_fit',
        "label": 'Особиста сумісність',
        "short": 'О',
        "explain": 'Важливість мотивації, переносимого стресу, відновлення, цінностей і self-respect.',
        "question": 'Наскільки для мене зараз важливо, щоб вибір не створював внутрішнього спротиву чи виснаження?',
    },
]

DOMAIN_BY_KEY = {d["key"]: d for d in DOMAINS}


AHP_DOMAIN_COPY = {
    "economic_quality": {
        "label": "Фінанси",
        "question": "Наскільки зараз критично для вас максимізувати дохідність, гарантувати стабільний cash flow та захистити капітал?",
        "description": "Це не про те, «чи любите ви гроші». Це про те, чи перебуваєте ви у фазі агресивного накопичення і потреби в ліквідності. Якщо ви оберете цей пріоритет, ви будете змушені відмовлятися від красивих, перспективних чи комфортних проєктів, якщо вони не дають чіткого і швидкого фінансового результату (IRR, ROI).",
    },
    "strategic_significance": {
        "label": "Стратегія",
        "question": "Наскільки важливо для вас (найближчі 1–2 роки) інвестувати у своє майбутнє (нові ніші, партнерства, репутацію, знання), навіть якщо це не дає швидкої фінансової віддачі?",
        "description": "Це ставка на довгострокову перевагу і «стратегічну позицію». Обравши цей пріоритет, ви погоджуєтеся тримати у портфелі проєкти, які можуть бути фінансово скромними сьогодні, але створюють для вас унікальну конкурентну перевагу, синергію з іншими бізнесами або відкривають двері в потрібні екосистеми завтра.",
    },
    "asset_controllability": {
        "label": "Керованість",
        "question": "Наскільки критично для вас мати тверді важелі впливу, абсолютну прозорість цифр та юридичну захищеність вашого капіталу?",
        "description": "Це про архітектуру влади: хто тримає штурвал і чи є у вас «стоп-кран». Наявність компетентної команди, юридичного права вето, доступу до об’єктивного аудиту та чіткого механізму виходу. Обравши цей пріоритет, ви погоджуєтеся відхиляти навіть найбільш надприбуткові пропозиції, якщо вони базуються лише на «чесному слові» і ставлять вас у позицію безправного пасажира, який не контролює ситуацію.",
    },
    "management_load": {
        "label": "Навантаження",
        "question": "Наскільки критично для вас зберегти час, увагу й ментальний ресурс для інших важливих напрямів?",
        "description": "Це питання альтернативної вартості. Кожна година вашої операційної залученості та мікроменеджменту — це втрачений час для іншого бізнесу, сім’ї або відновлення. Надаючи вагу цьому критерію, ви віддаєте перевагу проєктам із високим ступенем автономії, де результат досягається завдяки архітектурі процесів та системному управлінню, а не ручному втручанню і мікроменеджменту.",
    },
    "personal_fit": {
        "label": "Особиста сумісність",
        "question": "Наскільки критично, щоб діяльність давала вам енергію та не суперечила цінностям?",
        "description": "Це про якість енергії, а не кількість годин. Обравши цей пріоритет, ви відмовляєтеся від вигідних бізнесів, якщо вони створюють моральний компроміс, внутрішній спротив або дискомфорт від людей, з якими доведеться працювати.",
    },
}


AHP_DOMAIN_COLORS = {
    "economic_quality": {"dark": "#2E7D32", "medium": "#66BB6A", "light": "#C8E6C9"},
    "strategic_significance": {"dark": "#1565C0", "medium": "#42A5F5", "light": "#BBDEFB"},
    "asset_controllability": {"dark": "#6A1B9A", "medium": "#AB47BC", "light": "#E1BEE7"},
    "management_load": {"dark": "#0277BD", "medium": "#29B6F6", "light": "#B3E5FC"},
    "personal_fit": {"dark": "#00695C", "medium": "#26A69A", "light": "#B2DFDB"},
}

AHP_OPTION_COLOR_LEVEL = {
    "left_very_strong": "dark",
    "left_strong": "medium",
    "left_moderate": "light",
    "equal": "light",
    "right_moderate": "light",
    "right_strong": "medium",
    "right_very_strong": "dark",
}


PAIRWISE_OPTIONS = [
    ("left_very_strong", 7.0),
    ("left_strong", 5.0),
    ("left_moderate", 3.0),
    ("equal", 1.0),
    ("right_moderate", 1.0 / 3.0),
    ("right_strong", 1.0 / 5.0),
    ("right_very_strong", 1.0 / 7.0),
]

AHP_OPTION_LABELS = {
    # Labels are visually clean but internally unique via zero-width markers.
    # This prevents duplicate-label ambiguity in Streamlit radio rendering.
    "left_very_strong": "дуже сильно",
    "left_strong": "суттєво",
    "left_moderate": "помірно",
    "equal": "однаково",
    "right_moderate": "помірно",
    "right_strong": "суттєво",
    "right_very_strong": "дуже сильно",
}

PAIRWISE = [
    ("D01", "economic_quality", "strategic_significance"),
    ("D02", "economic_quality", "asset_controllability"),
    ("D03", "economic_quality", "management_load"),
    ("D04", "economic_quality", "personal_fit"),
    ("D05", "strategic_significance", "asset_controllability"),
    ("D06", "strategic_significance", "management_load"),
    ("D07", "strategic_significance", "personal_fit"),
    ("D08", "asset_controllability", "management_load"),
    ("D09", "asset_controllability", "personal_fit"),
    ("D10", "management_load", "personal_fit"),
]

PAIR_BY_SET = {frozenset((a, b)): pid for pid, a, b in PAIRWISE}
PAIR_LOOKUP = {pid: (left, right) for pid, left, right in PAIRWISE}

AHP_GROUPS = [
    ("Економічне ядро", ["D01", "D02", "D03", "D04"]),
    ("Стратегічний кластер", ["D05", "D06", "D07"]),
    ("Керованість / навантаження / особиста сумісність", ["D08", "D09", "D10"]),
]

# Dynamic AHP flow: start with Finance ↔ Load, then reveal the next comparison based on the previous answer.
AHP_FIRST_PAIR = "D03"  # economic_quality ↔ management_load
AHP_BASE_SEQUENCE = [AHP_FIRST_PAIR] + [pid for pid, _, _ in PAIRWISE if pid != AHP_FIRST_PAIR]

EMOTION_MEMO_NOTES = {
    "calm": "Поточний стан: спокійний. Додаткового попередження про шум немає.",
    "uncertain": "Поточний стан: невизначеність. Розглядай memo як структурований перший прохід; перед дією переглянь припущення.",
    "overloaded": "Поточний стан: перевантаження. Повтори перегляд після відновлення перед вкладенням капіталу або часу.",
    "excited": "Поточний стан: збудження. Перед дією перевір FOMO та надмірний оптимізм.",
    "stressed": "Поточний стан: стрес. Відокрем терміновість від важливості; повтори перегляд у нейтральному стані.",
    "tired": "Поточний стан: втома. Відклади незворотні дії до відновлення і повторно перевір ключові припущення.",
}

STATUS_ORDER = ["INVEST", "HOLD", "REFACTOR", "EXIT"]

# --- Structural contracts / constants -------------------------
DomainConfig: TypeAlias = dict[str, Any]
CriterionConfig: TypeAlias = dict[str, Any]
ScoreMap: TypeAlias = dict[str, float]

PAGE_WELCOME = "welcome"
PAGE_AHP = "ahp"
PAGE_BASKET = "basket"
PAGE_VETO = "veto"
PAGE_MCDA = "mcda"
PAGE_DASHBOARD = "dashboard"
PAGE_MEMO = "memo"
LEGACY_PAGE_CASE = "case"

PAGE_KEYS = {
    PAGE_WELCOME,
    PAGE_AHP,
    PAGE_BASKET,
    PAGE_VETO,
    PAGE_MCDA,
    PAGE_DASHBOARD,
    PAGE_MEMO,
}

DEFAULT_BASKET_KEY = "core"
BASKET_KEYS = {"core", "growth", "opportunity"}
SCALE_ANCHORS = [10, 7, 5, 3, 0]
AHP_CR_WARNING_THRESHOLD = 0.10
ACTIVE_ASSET_TYPES = {"operating business", "partnership", "growth venture"}

REQUIRED_DRAFT_KEYS = {
    "case_data",
    "ahp_answers",
    "veto_answers",
    "veto_notes",
    "mcda_answers",
    "mcda_notes",
}
ALLOWED_IMPORT_KEYS = {
    "case_data",
    "ahp_answers",
    "portfolio_basket",
    "veto_answers",
    "veto_notes",
    "mcda_answers",
    "mcda_notes",
    "counterargument",
    "current_step",
    "mcda_index",
}
EXPECTED_AHP_KEYS = {pid for pid, _, _ in PAIRWISE}
MEMO_DATETIME_FORMAT = "%Y-%m-%d %H:%M"
MEMO_FILENAME_DATETIME_FORMAT = "%Y%m%d_%H%M"
DEFAULT_MEMO_COUNTERARGUMENT = "- Not specified by user."
SCROLL_COMPONENT_SIZE = 1


VETO_ITEMS = [
    {"key": "financial_threshold", "name": "Фінансовий поріг", "description": "Актив у базовому сценарії не дає мінімально прийнятної дохідності або тримається лише на надто оптимістичних припущеннях.", "signal": "закрити / доопрацювати"},
    {"key": "strategic_clarity", "name": "Стратегічна ясність", "description": "Неможливо просто пояснити, для кого працює актив, на якому ринку він і за рахунок чого має виграти (Unfair Advantage - ?).", "signal": "доопрацювати"},
    {"key": "real_capacity", "name": "Реальна спроможність", "description": "Для успіху потрібні люди, компетенції, ресурси або зв’язки, яких зараз немає і які нереально швидко створити", "signal": "відкласти / доопрацювати"},
    {"key": "attention_price", "name": "Ціна для уваги", "description": "Актив забирає непропорційно багато часу, уваги й управлінської енергії порівняно з очікуваною користю", "signal": "доопрацювати"},
    {"key": "no_exit_rules", "name": "Відсутність правил виходу", "description": "До старту неможливо чітко визначити, за яких умов актив треба зупинити, продати або закрити.", "signal": "відкласти"},
    {"key": "sunk_cost_trap", "name": "Пастка вже вкладеного", "description": "Рішення продовжувати тримається переважно на тому, що вже вкладено багато грошей, часу чи зусиль. (sunk cost)", "signal": "відкласти / зовнішній перегляд"},
    {"key": "model_fragility", "name": "Крихкість моделі", "description": "Один сильний удар — втрата ключового клієнта, партнера, постачальника або фінансування — робить актив нежиттєздатним.", "signal": "доопрацювати"},
    {"key": "noisy_decision", "name": "Шумне рішення", "description": "Власник у різний час оцінює актив радикально по-різному через настрій, втому чи подачу інформації.", "signal": "відкласти"},
    {"key": "owner_goal_conflict", "name": "Конфлікт із цілями власника", "description": "Актив може приносити гроші, але суперечить цінностям, репутації або бажаному способу життя власника", "signal": "закрити / доопрацювати"},
    {"key": "risk_concentration", "name": "Небезпечна концентрація ризику", "description": "Актив надто збільшує частку капіталу, боргу або неліквідності в одному місці й робить увесь портфель вразливим.", "signal": "доопрацювати / розділити ставку"},
]


VETO_BY_KEY = {item["key"]: item for item in VETO_ITEMS}
EXPECTED_VETO_KEYS = {item["key"] for item in VETO_ITEMS}

VETO_RISK_GROUPS = [
    {
        "title": "Фінансова життєздатність",
        "description": "Перевірка, чи актив економічно витримує базовий сценарій і не створює надмірної концентрації ризику.",
        "items": [
            ("financial_threshold", "Hard stop"),
            ("model_fragility", "Review"),
            ("risk_concentration", "Review"),
        ],
    },
    {
        "title": "Стратегічна / операційна спроможність",
        "description": "Перевірка, чи зрозуміло, як актив має виграти, і чи є реальні ресурси для виконання.",
        "items": [
            ("strategic_clarity", "Review"),
            ("real_capacity", "Review"),
            ("attention_price", "Review"),
        ],
    },
    {
        "title": "Поведінкові та особисті ризики",
        "description": "Перевірка пасток мислення, шуму рішення, конфлікту з цілями власника та правил виходу.",
        "items": [
            ("sunk_cost_trap", "Behavioral risk"),
            ("noisy_decision", "Behavioral risk"),
            ("owner_goal_conflict", "Hard stop"),
            ("no_exit_rules", "Review"),
        ],
    },
]

VETO_SEVERITY_LABELS = {
    "Hard stop": "Hard stop",
    "Review": "Review",
    "Behavioral risk": "Behavioral risk",
}

VETO_SEVERITY_CLASS = {
    "Hard stop": "hard",
    "Review": "review",
    "Behavioral risk": "behavior",
}

REVIEW_PROTOCOLS = [
    {
        "size": "0–2.5%",
        "mode": "Рутинне / експериментальне рішення",
        "action": "Короткий перегляд",
        "validation": "24h cooling-off, базовий Decision Log, перевірка stop-факторів. Рішення можна приймати автономно, але лише після паузи для зниження впливу настрою, втоми або ситуативного шуму.",
    },
    {
        "size": "2.5–12.5%",
        "mode": "Базове інвестиційне рішення",
        "action": "Явний перегляд",
        "validation": "Рішення розбивається на ключові компоненти: економіка, ризик, навантаження, контроль. Метрики перевіряються до фінального висновку, щоб не підганяти аргументи під уже бажане рішення.",
    },
    {
        "size": "12.5–50%",
        "mode": "Стратегічне рішення",
        "action": "Поглиблений перегляд",
        "validation": "Обов’язкові stress test, premortem / reverse thinking, сценарій поганого результату. До рішення фіксуються kill criteria: конкретні стани й дати, за яких актив треба змінити або закрити.",
    },
    {
        "size": ">50%",
        "mode": "Концентрація ризику",
        "action": "Зовнішній аудит",
        "validation": "Red-teaming і незалежна перевірка. Рішення має бути захищене перед зовнішніми опонентами, де ціль — не підтримати ідею, а знайти її слабкі місця.",
    },
]

REVIEW_PROTOCOL_NOTE = (
    "Чим більший розмір рішення відносно портфеля, тим жорсткішою стає процедура перевірки. "
    "Модель не забороняє великі ставки, але вимагає вищої дисципліни: паузи, декомпозиції, "
    "стрес-тесту, kill criteria та зовнішнього заперечення."
)

BASKET_CONFIG = {
    "core": {
        "label": "Core Holdings",
        "description": "Активи, які мають стабільно підтримувати фінансову базу портфеля без значного залучення власника. Core може мати нижчий upside, але має бути стабільним, ліквідним і мало забирати увагу.",
        "thresholds": {"invest": 75, "hold": 60, "refactor": 50},
        "threshold_line": "INVEST ≥75 | HOLD 60–74.9 | REFACTOR 50–59.9 | EXIT <50",
    },
    "growth": {
        "label": "Growth Ventures",
        "description": "Активи, на які робиться стратегічна ставка для зростання капіталу. Growth має вищий поріг, бо там більше ризику, активної участі й очікуваної віддачі.",
        "thresholds": {"invest": 80, "hold": 70, "refactor": 60},
        "threshold_line": "INVEST ≥80 | HOLD 70–79.9 | REFACTOR 60–69.9 | EXIT <60",
    },
    "opportunity": {
        "label": "Opportunity Fund",
        "description": "Активи або ідеї, які тестуються як асиметричні можливості. Opportunity має найвищий admission threshold: туди не можна пускати цікаві, але сирі ідеї.",
        "thresholds": {"invest": 85, "hold": 75, "refactor": 55},
        "threshold_line": "INVEST ≥85 | HOLD 75–84.9 | REFACTOR 55–74.9 | EXIT / NO-GO — за Kill Criteria",
    },
}


def basket_threshold_line(bkey: str) -> str:
    """Return the threshold line for a portfolio basket key."""
    cfg = BASKET_CONFIG.get(bkey, BASKET_CONFIG["core"])
    return cfg.get("threshold_line", "")


CRITERIA = [
    {
        "key": "irr",
        "domain": "economic_quality",
        "name": "Очікувана дохідність / IRR / ROI",
        "type": "scale",
        "default": None,
        "what": "Наскільки реалістично та ймовірно, що цей напрям, актив або можливість досягне цільової фінансової віддачі у базовому сценарії, спираючись на якість моделі доходу та перевіреність припущень.",
        "anchors": {
            "10": "Висока ймовірність досягти або перевищити цільову дохідність; базовий сценарій сильний, фінансова логіка підтверджена фактами, припущення перевірені.",
            "7": "Дохідність виглядає реалістичною; є кілька залежностей або невідомих змінних, але вони зрозумілі й керовані.",
            "5": "Прийнятна дохідність можлива, але не гарантована; результат сильно залежить від 1–2 ключових припущень.",
            "3": "Цільова дохідність більше схожа на optimistic case; базовий сценарій слабкий, нестабільний або недостатньо підтверджений.",
            "0": "Немає достатніх підстав очікувати цільову дохідність; фінансовий результат тримається на надії, бонусах або випадковості.",
        },
        "evidence": "Базовий сценарій, фінансову модель, історичні дані або traction, якість припущень про доходи й витрати, ймовірність досягнення цільової IRR/ROI без екстремального оптимізму.",
    },
    {
        "key": "cash_flow_quality",
        "domain": "economic_quality",
        "name": "Якість cash flow",
        "type": "scale",
        "default": 5.0,
        "what": "Передбачуваність, повторюваність, волатильність і видимість грошового потоку.",
        "anchors": {"10": "Стабільний, повторюваний, добре прогнозований cash flow; короткий cash conversion cycle; мало сюрпризів.", "7": "Загалом хороший, але є циклічність або кілька слабких місць.", "5": "Гроші є, але вони нерівні, погано видимі або сильно залежать від ручного управління.", "3": "Cash flow нервовий, рваний, із частими касовими провалами.", "0": "Майже немає довіри до потоку грошей."},
        "evidence": "Якість грошей: повторюваність, видимість, волатильність, цикл конвертації в cash flow.",
    },
    {
        "key": "liquidity_reversibility",
        "domain": "economic_quality",
        "name": "Ліквідність і зворотність виходу",
        "type": "scale",
        "default": 5.0,
        "what": "Наскільки швидко і з яким економічним дисконтом можна вийти, продати або згорнути позицію.",
        "anchors": {"10": "Вийти можна швидко, дешево і майже без permanent damage.", "7": "Вихід можливий, але з певним дисконтом, тертям або часовою затримкою.", "5": "Вийти можна, але боляче і не швидко.", "3": "Ліквідність слабка; unwind дорогий або складний.", "0": "Фактично пастка: вийти дуже важко або майже неможливо."},
        "evidence": "Економічна ціна виходу.",
    },
    {
        "key": "downside_resilience",
        "domain": "economic_quality",
        "name": "Стійкість до просадки",
        "type": "scale",
        "default": 5.0,
        "what": "Здатність пережити шок і обмежити permanent loss.",
        "anchors": {"10": "Актив добре переживає шоки; downside обмежений; конструкція міцна.", "7": "Сильний стрес переживе, але з відчутною втратою темпу або маржі.", "5": "Середня стійкість; кілька слабких місць, але не критичних.", "3": "Один серйозний удар може сильно пошкодити актив.", "0": "Крихка конструкція; downside асиметрично поганий."},
        "evidence": "Борг і постійні витрати; концентрація клієнтів; валютний, товарний або регуляторний ризик; грошовий резерв; єдина точка відмови.",
    },
    {
        "key": "future_moves",
        "domain": "strategic_significance",
        "name": "Майбутні ходи",
        "type": "scale",
        "default": 5.0,
        "what": "Чи відкриває доступ до ринків, клієнтів, партнерів, знань або можливостей, які інакше були б недоступні?",
        "anchors": {"10": "Відкриває багато сильних траєкторій на 12–36 міс.: нові ринки, ролі, партнерства, deal flow, сценарії pivot.", "7": "Відкриває кілька реальних наступних ходів.", "5": "Дає обмежену, але корисну майбутню гнучкість.", "3": "Майже не створює нових ходів або створює слабкі опції.", "0": "Фіксує в жорсткій траєкторії, звужує маневр."},
        "evidence": "Конкретні майбутні сценарії, право без зобов’язання, нові ринки, deal flow, опції pivot.",
    },
    {
        "key": "internal_strengthening",
        "domain": "strategic_significance",
        "name": "Внутрішнє посилення",
        "type": "scale",
        "default": 5.0,
        "what": "Чи нарощує переносимі компетенції, системи, знання або управлінську силу, які залишаться навіть після виходу.",
        "anchors": {"10": "Сильно прокачує власника / систему; після цього ти стаєш помітно сильнішим.", "7": "Дає важливі переносимі навички або системи.", "5": "Локальна користь є, але обмежена.", "3": "Дає мало нового; переважно операційна рутина.", "0": "Чорний ящик: результат є, але ти не стаєш сильнішим."},
        "evidence": "Нові управлінські навички, розуміння механіки, reusable systems, IP, playbooks, здатність повторити результат в іншому контексті.",
    },
    {
        "key": "current_position_strength",
        "domain": "strategic_significance",
        "name": "Сила позиції зараз",
        "type": "scale",
        "default": 5.0,
        "what": "Чи підсилює те, що вже є: активи, кар’єру, клієнтів, команду, канали, репутаційний контур.",
        "anchors": {"10": "Сильний мультиплікатор для поточної системи.", "7": "Є відчутне підсилення.", "5": "Локальна користь.", "3": "Майже ізольована зона.", "0": "Відтягує ресурси або шкодить системі."},
        "evidence": "Перехресні продажі, спільні канали, клієнти, команда, дані, репутаційний ефект для наявних зон.",
    },
    {
        "key": "management_influence",
        "domain": "asset_controllability",
        "name": "Управлінський вплив",
        "type": "scale",
        "default": 5.0,
        "what": "Твій реальний вплив на ключові рішення, курс і результат у цьому активі / ролі / можливості.",
        "anchors": {"10": "Можеш змінювати ключові рішення і результат.", "7": "Вплив великий, але не повний.", "5": "Вплив частковий і нерівний.", "3": "Вплив обмежений; багато залежить від інших.", "0": "Відповідальність без контролю."},
        "evidence": "Право змінити курс, кадровий вплив, участь у ключових рішеннях, сила голосу в партнерстві.",
    },
    {
        "key": "team_quality",
        "domain": "asset_controllability",
        "name": "Якість команди",
        "type": "scale",
        "default": 5.0,
        "what": "Якість людей, від яких залежить виконання: команда, партнери, менеджмент, керівник або операційний контур.",
        "anchors": {"10": "Сильна, зріла, чесна, швидка, автономна команда.", "7": "Команда загалом сильна, але є окремі прогалини в автономності, швидкості або зрілості.", "5": "Середня команда; працює, але потребує багато коригувань.", "3": "Слабка, повільна або нестабільна команда.", "0": "Токсична, некомпетентна або ненадійна команда."},
        "evidence": "Команда, партнери, менеджмент, операційний контур, здатність тягнути без ручного контролю.",
    },
    {
        "key": "governance_transparency",
        "domain": "asset_controllability",
        "name": "Прозорість і правила управління",
        "type": "scale",
        "default": 5.0,
        "what": "Наскільки прозорі правила, цифри, права, обов’язки, звітність і захист твоїх інтересів.",
        "anchors": {"10": "Повна прозорість: є доступ до цифр, зрозумілі правила, формальні права, регулярна звітність і сильний захист інтересів.", "7": "Загалом прозоро й контрольовано; є дрібні сірі зони, але вони не критичні.", "5": "Базова прозорість є, але частина інформації, правил або прав залишається нечіткою.", "3": "Багато неясності: слабка звітність, неповні цифри, нечіткі домовленості або слабкий захист.", "0": "Непрозорість, хаос, усні домовленості, юридична вразливість або неможливість перевірити реальний стан справ."},
        "evidence": "Договори, умови партнерства, звітність, доступ до P&L / cash flow, права голосу, право veto, можливість аудиту, правила виходу, відповідальність сторін.",
    },
    {
        "key": "time_load_fit",
        "domain": "management_load",
        "name": "Часове навантаження",
        "type": "cost",
        "input_label": "Фактична витрата часу на тиждень",
        "ideal_label": "Комфортні / бажані години на тиждень",
        "worst_label": "Найгірше допустиме навантаження",
        "default": {"value": "", "ideal": "", "worst": ""},
        "what": "Введи реальну витрату часу на тиждень, комфортний цільовий рівень і найгірше допустиме навантаження.",
        "anchors": {"10": "0 або близько до 0 год/тиждень у стабільному режимі.", "7": "Помірне навантаження, яке не з’їдає фокус.", "5": "Прийнятно, але актив уже помітно конкурує за час.", "3": "Високе навантаження, яке витісняє інші активи.", "0": "Найгірше допустиме або вище; потрібне доопрацювання / перегляд стоп-факторів."},
        "evidence": "Бери реальну середню за останні 8–12 тижнів для чинного активу. Для нового — очікуваний стабільний режим, а не стартовий спринт.",
    },
    {
        "key": "cognitive_load_fit",
        "domain": "management_load",
        "name": "Когнітивне навантаження",
        "type": "scale",
        "default": 5.0,
        "what": "Скільки фонової уваги актив забирає поза прямою роботою?",
        "anchors": {"10": "Майже не засмічує голову; low switching cost.", "7": "Іноді потребує уваги, але не окуповує свідомість.", "5": "Регулярно висить у фоні і відволікає.", "3": "Постійно висмоктує ментальний ресурс.", "0": "Нав’язливий актив, який краде мислення і фокус."},
        "evidence": "Як часто думаєш про нього поза роботою?",
    },
    {
        "key": "context_switching_fit",
        "domain": "management_load",
        "name": "Вартість перемикання контексту",
        "type": "scale",
        "default": 5.0,
        "what": "Наскільки часто актив вимагає термінових втручань, перемикань і реакцій поза запланованим часом?",
        "anchors": {"10": "Майже не висмикує; усе планово.", "7": "Іноді висмикує, але контрольовано.", "5": "Регулярно створює дрібні перемикання.", "3": "Часто ламає графік і фокус.", "0": "Живе в режимі пожеж, постійно перебиває інші активи."},
        "evidence": "Чи перебиває стратегічне мислення? Чи вимагає частого context switching?",
    },
    {
        "key": "motivation_fit",
        "domain": "personal_fit",
        "name": "Мотиваційна сумісність",
        "type": "scale",
        "default": 5.0,
        "what": "Чи є спокійний живий інтерес починати і повертатися до цього активу?",
        "anchors": {"10": "Сильне природне тяжіння; хочеться лізти в тему.", "7": "Стабільний інтерес і позитивний pull.", "5": "Нейтрально; можу, але без внутрішнього вогню.", "3": "Треба себе штовхати, щоб займатися цим.", "0": "Відраза або хронічне уникання."},
        "evidence": "Не плутати з FOMO, азартом або бажанням “не втратити шанс”.",
    },
    {
        "key": "stress_fit",
        "domain": "personal_fit",
        "name": "Стресова сумісність",
        "type": "scale",
        "default": 5.0,
        "what": "Чи сумісний тип стресу під час роботи з твоєю нервовою системою?",
        "anchors": {"10": "Стрес робочий, мобілізує, не ламає.", "7": "Напружено, але контрольовано.", "5": "Стрес відчутний і потребує компенсації.", "3": "Регулярне перевантаження або нездоровий фон.", "0": "Тип стресу для тебе токсичний."},
        "evidence": "Конфлікти, пожежі, невизначеність, репутаційний тиск.",
    },
    {
        "key": "recovery_fit",
        "domain": "personal_fit",
        "name": "Відновлення",
        "type": "scale",
        "default": 5.0,
        "what": "Як ти відновлюєшся після взаємодії з активом?",
        "anchors": {"10": "Втома приємна, легко відновлюється.", "7": "Є втома, але вона відновлюється.", "5": "Помітне виснаження; recovery середній.", "3": "Важко відновитися навіть після паузи.", "0": "Залишається токсичний післясмак і виснаження."},
        "evidence": "“Втомлений, але живий” vs “розбитий”.",
    },
    {
        "key": "identity_values_fit",
        "domain": "personal_fit",
        "name": "Ціннісна та рольова сумісність",
        "type": "scale",
        "default": 5.0,
        "what": "Чи сумісний актив із твоїми цінностями, self-respect і образом себе поза моментом вигоди.",
        "anchors": {"10": "Повна внутрішня узгодженість.", "7": "Загалом сумісний, є дрібні компроміси.", "5": "Нейтрально; без особливої гордості чи сорому.", "3": "Внутрішня неузгодженість або рольовий дисонанс.", "0": "Сором, самообман або прямий конфлікт із цінностями."},
        "evidence": "Не плутати з престижністю. Чи хочеш бути людиною, яка цим володіє / цим займається?",
    },
]

CRITERIA_BY_KEY = {c["key"]: c for c in CRITERIA}


CSS = """
<style>
/* ============================================================
   Decision Framework – Design System v2.0
   Single source of truth. No version stacking.
   ============================================================ */

/* --- Tokens ------------------------------------------------ */
:root {
  --bg:           #f5f7fa;
  --surface:      #ffffff;
  --surface-soft: #f8fafc;
  --border:       #e4e8ef;
  --border-strong:#c9d3e0;
  --text-main:    #0f172a;
  --text-body:    #334155;
  --text-muted:   #64748b;
  --text-hint:    #94a3b8;
  --accent:       #1e3a5f;
  --accent-hover: #162e4d;
  --accent-ring:  rgba(30,58,95,0.14);
  --green-bg:     #f0fdf4;
  --green-border: #bbf7d0;
  --green-text:   #047857;
  --amber-bg:     #fffbeb;
  --amber-border: #fde68a;
  --amber-text:   #92400e;
  --red-bg:       #fff7f7;
  --red-border:   #fecaca;
  --red-text:     #b42318;
  --radius-sm:    10px;
  --radius-md:    14px;
  --radius-lg:    18px;
  --radius-xl:    22px;
  --shadow-card:  0 2px 10px rgba(15,23,42,0.04);
}

/* --- Base -------------------------------------------------- */
html, body, [data-testid="stAppViewContainer"], .stApp {
  background: var(--bg) !important;
  font-family: Inter, system-ui, -apple-system, sans-serif !important;
  font-size: 17px !important;
}
.block-container {
  max-width: 1320px !important;
  padding: 3.5rem 2.5rem 4rem 2.5rem !important;
}
@media (max-width: 820px) {
  .block-container { padding: 2.5rem 1rem 3rem 1rem !important; }
}


/* --- Force readable light theme on deployed Streamlit --------
   Streamlit Cloud may inherit dark theme tokens from user/browser settings.
   The app uses a custom light design system, so native Streamlit text must be
   explicitly reset to dark colors on light surfaces. */
.stApp,
.stApp p,
.stApp li,
.stApp label,
.stApp span,
.stApp div[data-testid="stMarkdownContainer"],
.stApp div[data-testid="stMarkdownContainer"] p {
  color: var(--text-body) !important;
}
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp h6,
.stApp div[data-testid="stMarkdownContainer"] h1,
.stApp div[data-testid="stMarkdownContainer"] h2,
.stApp div[data-testid="stMarkdownContainer"] h3,
.stApp div[data-testid="stMarkdownContainer"] h4,
.stApp div[data-testid="stMarkdownContainer"] h5,
.stApp div[data-testid="stMarkdownContainer"] h6 {
  color: var(--text-main) !important;
}
div[data-testid="stExpander"] details {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-card) !important;
}
div[data-testid="stExpander"] details summary,
div[data-testid="stExpander"] details summary * {
  color: var(--text-main) !important;
  font-weight: 680 !important;
}
div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
  background: var(--surface) !important;
  color: var(--text-body) !important;
}
div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] p,
div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] label,
div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] label p,
div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] label p {
  color: var(--text-body) !important;
}

/* --- Generic cards ---------------------------------------- */
.df-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  margin: 10px 0 14px 0;
  box-shadow: var(--shadow-card);
}
.df-card h3 { margin: 0 0 6px 0; font-size: 17px; font-weight: 650; }
.df-card.df-green { background: var(--green-bg); border-color: var(--green-border); }
.df-card.df-amber { background: var(--amber-bg); border-color: var(--amber-border); }
.df-card.df-red   { background: var(--red-bg);   border-color: var(--red-border);   }
.df-small { color: var(--text-muted); font-size: 15px; }

/* --- Page header ------------------------------------------ */
.df-prem-page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 10px;
}
.df-prem-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.022em;
  line-height: 1.2;
}
.df-prem-meta { margin-top: 3px; font-size: 15px; font-weight: 500; color: var(--text-muted); }
.df-prem-completion {
  font-size: 14px; font-weight: 640; padding: 5px 9px;
  border: 1px solid var(--border); color: var(--text-muted);
  background: var(--surface); border-radius: 999px; white-space: nowrap;
}

/* --- Progress bar ----------------------------------------- */
.df-prem-progress {
  width: 100%; height: 5px; border-radius: 999px;
  background: var(--border); overflow: hidden; margin: 10px 0 22px 0;
}
.df-prem-progress-fill { height: 100%; border-radius: 999px; background: var(--accent); }

/* --- Domain intro card ------------------------------------ */
.df-prem-domain-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-xl); padding: 18px 22px;
  margin-bottom: 20px; box-shadow: var(--shadow-card);
}
.df-prem-domain-title { font-size: 19px; font-weight: 680; color: var(--text-main); margin-bottom: 4px; }
.df-prem-domain-subtitle { font-size: 16px; line-height: 1.5; color: var(--text-muted); max-width: 820px; }

/* --- Criterion container ---------------------------------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-xl) !important;
  background: var(--surface) !important;
  box-shadow: var(--shadow-card) !important;
  padding: 14px 18px !important;
  margin: 10px 0 12px 0 !important;
}

/* --- Criterion header ------------------------------------- */
.df-prem-criterion-head {
  display: flex; justify-content: space-between;
  align-items: flex-start; gap: 16px; margin-bottom: 12px;
}
.df-prem-criterion-title { font-size: 18px; font-weight: 660; color: var(--text-main); letter-spacing: -0.01em; }
.df-prem-criterion-desc { font-size: 15.5px; line-height: 1.5; color: var(--text-muted); margin-top: 4px; max-width: 840px; }

/* --- Status badges ---------------------------------------- */
.df-prem-status {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 13.5px; font-weight: 640; border-radius: 999px;
  padding: 4px 9px; white-space: nowrap;
  border: 1px solid var(--border); color: var(--text-muted); background: var(--surface-soft);
}
.df-prem-status.done    { border-color: var(--green-border); color: var(--green-text); background: var(--green-bg); }
.df-prem-status.missing { border-color: var(--amber-border); color: var(--amber-text); background: var(--amber-bg); }
.df-prem-status.error   { border-color: var(--red-border);   color: var(--red-text);   background: var(--red-bg);   }
.df-prem-status.progress{ border-color: var(--amber-border); color: var(--amber-text); background: var(--amber-bg); }

/* --- Hint / evidence block -------------------------------- */
.df-prem-hint {
  background: var(--surface-soft); border: 1px solid #edf0f4;
  border-radius: var(--radius-md); padding: 9px 12px; margin-top: 12px;
  font-size: 15px; color: var(--text-muted); line-height: 1.45;
}
.df-prem-hint.df-prem-error { background: var(--red-bg); border-color: var(--red-border); color: var(--red-text); }
.df-prem-nav-spacer { height: 8px; }
.df-field-error { font-size: 14px; font-weight: 500; color: var(--red-text); margin-top: 5px; }

/* --- KPI tiles -------------------------------------------- */
.df-kpi {
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: 16px 18px; background: var(--surface); box-shadow: var(--shadow-card);
}
.df-kpi .value { font-size: 2rem; font-weight: 780; line-height: 1.1; color: var(--text-main); }
.df-kpi .label { color: var(--text-muted); font-size: 14.5px; font-weight: 500; margin-bottom: 4px; }

/* ============================================================
   MCDA ANCHOR CARDS (green -> red scale)
   ============================================================ */
div[data-testid="stRadio"] > label,
div[data-testid="stRadio"] label[data-testid="stWidgetLabel"] { display: none !important; }

div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] {
  display: grid !important;
  grid-template-columns: repeat(5, minmax(0, 1fr)) !important;
  gap: 10px !important; width: 100% !important;
  margin: 10px 0 0 0 !important; overflow: visible !important;
  align-items: stretch !important;
}

div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label {
  position: relative !important;
  min-height: 170px !important;
  height: 100% !important;
  align-self: stretch !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 18px 16px 16px 20px !important;
  background: var(--surface) !important;
  display: flex !important; align-items: flex-start !important;
  justify-content: flex-start !important; text-align: left !important;
  cursor: pointer !important; overflow: hidden !important;
  transition: border-color .13s ease, box-shadow .13s ease, transform .13s ease !important;
  box-shadow: none !important;
}

div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label::before {
  content: ""; position: absolute; left: 0; top: 0; bottom: 0;
  width: 4px; border-radius: 4px 0 0 4px;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label:nth-of-type(1)::before { background: #22c55e; }
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label:nth-of-type(2)::before { background: #84cc16; }
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label:nth-of-type(3)::before { background: #f59e0b; }
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label:nth-of-type(4)::before { background: #f97316; }
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label:nth-of-type(5)::before { background: #ef4444; }

div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label:hover {
  border-color: var(--border-strong) !important;
  box-shadow: 0 4px 14px rgba(15,23,42,0.07) !important;
  transform: translateY(-1px) !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label:has(input:checked),
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label:has([aria-checked="true"]) {
  border: 2px solid var(--accent) !important;
  background: #f3f7fc !important;
  box-shadow: 0 0 0 3px var(--accent-ring), 0 5px 16px rgba(15,23,42,0.06) !important;
  transform: none !important;
}
/* Selected MCDA card: keep only the strong contour; no dot/checkmark marker. */
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label:has(input:checked)::after,
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label:has([aria-checked="true"])::after {
  display: none !important;
  content: none !important;
}

/* Hide native radio controls */
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] input[type="radio"],
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] svg,
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] [data-testid="stRadioIcon"],
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label > div:first-child:not(:last-child),
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label > span:first-child:not(:last-child) { display: none !important; }

div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label p,
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label div[data-testid="stMarkdownContainer"] p {
  margin: 0 !important; padding-right: 20px !important;
  font-size: 15px !important; line-height: 1.42 !important;
  font-weight: 500 !important; color: var(--text-body) !important;
  white-space: normal !important; word-break: normal !important; overflow-wrap: break-word !important;
}

@media (max-width: 1200px) {
  div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] { grid-template-columns: repeat(3, minmax(0, 1fr)) !important; }
}
@media (max-width: 780px) {
  div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] { grid-template-columns: 1fr !important; }
  div[data-testid="stRadio"] [role="radiogroup"][aria-label^="MCDA anchor"] label { min-height: 92px !important; height: auto !important; }
}

/* ============================================================
   AHP COMPARISON CARDS
   ============================================================ */
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] {
  display: grid !important;
  grid-template-columns: repeat(7, minmax(0, 1fr)) !important;
  gap: 6px !important; width: 100% !important;
  margin: 4px 0 7px 0 !important; overflow: visible !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] label {
  min-height: 46px !important; min-width: 0 !important; box-sizing: border-box !important;
  border: 1.5px solid var(--border) !important; border-radius: var(--radius-md) !important;
  padding: 0 4px !important; background: var(--surface) !important;
  display: grid !important; place-items: center !important;
  text-align: center !important; overflow: hidden !important;
  cursor: pointer !important; transition: border-color .12s ease, box-shadow .12s ease !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] label:hover {
  border-color: var(--accent) !important; box-shadow: 0 2px 10px rgba(15,23,42,0.07) !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] label:has(input:checked) {
  border: 2.5px solid var(--accent) !important;
  background: #f3f7fc !important; box-shadow: 0 0 0 3px var(--accent-ring) !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] input[type="radio"],
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] svg,
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] [data-testid="stRadioIcon"],
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] label > div:first-child:not([data-testid="stMarkdownContainer"]),
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] label > span:first-child:not(:last-child) { display: none !important; }
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] label [data-testid="stMarkdownContainer"],
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] label [data-testid="stMarkdownContainer"] > div {
  width: 100% !important; height: 100% !important; margin: 0 !important; padding: 0 !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
  text-align: center !important; overflow: hidden !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] label p,
div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] label span {
  margin: 0 !important; padding: 0 !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
  width: 100% !important; height: 100% !important;
  font-size: 14.5px !important; font-weight: 660 !important;
  line-height: 1.05 !important; letter-spacing: -0.02em !important;
  white-space: nowrap !important; word-break: keep-all !important; overflow: hidden !important;
  text-overflow: clip !important; color: var(--text-body) !important; text-align: center !important;
}
@media (max-width: 1200px) {
  div[data-testid="stRadio"] [role="radiogroup"][aria-label^="AHP strength"] { grid-template-columns: repeat(4, minmax(0, 1fr)) !important; }
}

/* --- AHP button implementation: colored side strips ---------- */
div[class*="st-key-ahp_choice_"] div[data-testid="stButton"] button {
  position: relative !important;
  overflow: hidden !important;
  min-height: 46px !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  background: var(--surface) !important;
  color: var(--text-body) !important;
  font-size: 14.5px !important;
  font-weight: 660 !important;
  line-height: 1.05 !important;
  letter-spacing: -0.02em !important;
  box-shadow: none !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  padding: 0 10px !important;
}
div[class*="st-key-ahp_choice_"] div[data-testid="stButton"] button:hover {
  border-color: var(--accent) !important;
  box-shadow: 0 2px 10px rgba(15,23,42,0.07) !important;
}
div[class*="st-key-ahp_choice_"] div[data-testid="stButton"] button::before,
div[class*="st-key-ahp_choice_"] div[data-testid="stButton"] button::after {
  content: "" !important;
  position: absolute !important;
  top: 0 !important;
  bottom: 0 !important;
  width: 4px !important;
  pointer-events: none !important;
}
div[class*="st-key-ahp_choice_"] div[data-testid="stButton"] button::before {
  left: 0 !important;
  background: var(--ahp-left-strip, transparent) !important;
  border-radius: var(--radius-md) 0 0 var(--radius-md) !important;
}
div[class*="st-key-ahp_choice_"] div[data-testid="stButton"] button::after {
  right: 0 !important;
  background: var(--ahp-right-strip, transparent) !important;
  border-radius: 0 var(--radius-md) var(--radius-md) 0 !important;
}

/* ============================================================
   PORTFOLIO ROLE CARDS
   ============================================================ */
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] {
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  gap: 14px !important; width: 100% !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] label {
  position: relative !important; min-height: 240px !important;
  border: 1px solid var(--border) !important; border-radius: var(--radius-xl) !important;
  padding: 20px 22px !important; background: var(--surface) !important;
  display: flex !important; align-items: flex-start !important;
  justify-content: flex-start !important; text-align: left !important;
  cursor: pointer !important; transition: all .13s ease !important; box-shadow: var(--shadow-card) !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] label:hover {
  border-color: var(--border-strong) !important;
  box-shadow: 0 6px 20px rgba(15,23,42,0.08) !important; transform: translateY(-1px) !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] label:has(input:checked) {
  border: 2px solid var(--accent) !important; background: #f3f7fc !important;
  box-shadow: 0 0 0 3px var(--accent-ring) !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] label:has(input:checked)::after {
  content: "\2713"; position: absolute; top: 14px; right: 16px;
  width: 24px; height: 24px; border-radius: 999px;
  background: var(--accent); color: white; text-align: center;
  line-height: 24px; font-weight: 800;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] input[type="radio"],
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] svg,
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] [data-testid="stRadioIcon"],
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] label > div:first-child:not(:last-child),
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] label > span:first-child:not(:last-child) { display: none !important; }
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] label p:first-of-type {
  font-size: 1.15rem !important; font-weight: 780 !important;
  color: var(--text-main) !important; margin-bottom: 10px !important;
}
div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] label p:not(:first-of-type) {
  font-size: 15.5px !important; color: var(--text-body) !important; line-height: 1.5 !important;
}
@media (max-width: 900px) {
  div[data-testid="stRadio"] [role="radiogroup"][aria-label="Portfolio role"] { grid-template-columns: 1fr !important; }
}

/* ============================================================
   NUMERIC INPUTS
   ============================================================ */
div[data-testid="stNumberInput"] {
  background: transparent !important; border: 0 !important;
  border-radius: 0 !important; padding: 0 !important; box-shadow: none !important;
}
div[data-testid="stNumberInput"] label p {
  font-size: 14.5px !important; font-weight: 580 !important;
  color: var(--text-muted) !important; margin-bottom: 6px !important;
}
div[data-testid="stNumberInput"] input {
  min-height: 48px !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important; background: var(--surface) !important;
  text-align: center !important; font-size: 24px !important; font-weight: 720 !important;
  color: var(--text-main) !important; box-shadow: none !important;
  transition: border-color .13s ease, box-shadow .13s ease !important;
}
div[data-testid="stNumberInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-ring) !important; outline: none !important;
}
div[data-testid="stNumberInput"] button { display: none !important; }
div[data-testid="stNumberInput"] input::-webkit-outer-spin-button,
div[data-testid="stNumberInput"] input::-webkit-inner-spin-button { -webkit-appearance: none !important; }
div[data-testid="stNumberInput"] input[type="number"] { -moz-appearance: textfield !important; }

/* ============================================================
   TEXT INPUTS (IRR benefit fields)
   ============================================================ */
.df-finance-value-group { margin: 18px 0 22px 0; padding-bottom: 18px; position: relative; overflow: visible !important; }
.df-finance-value-group div[data-testid="column"] { position: relative; }
.df-finance-value-group div[data-testid="column"]:not(:last-child)::after {
  content: ""; position: absolute; right: -13px; top: 46px;
  width: 13px; height: 1px; background: var(--border-strong); z-index: 0;
}
@media (max-width: 820px) {
  .df-finance-value-group div[data-testid="column"]:not(:last-child)::after { display: none; }
}
div[data-testid="stTextInput"] { overflow: visible !important; padding-bottom: 12px !important; }
div[data-testid="stTextInput"] > div,
div[data-testid="stTextInput"] div[data-baseweb="input"] { overflow: visible !important; }
div[data-testid="stTextInput"] label p {
  font-size: 14.5px !important; font-weight: 580 !important;
  color: var(--text-muted) !important; margin-bottom: 6px !important;
}
div[data-testid="stTextInput"] input {
  min-height: 66px !important; height: 66px !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important; background: var(--surface) !important;
  font-size: 24px !important; font-weight: 720 !important;
  color: var(--text-main) !important; text-align: center !important;
  line-height: 1.1 !important; padding: 8px 12px 12px 12px !important; box-sizing: border-box !important;
  transition: border-color .13s ease, box-shadow .13s ease !important; box-shadow: none !important;
}
div[data-testid="stTextInput"] input::placeholder {
  font-size: 18px !important; font-weight: 400 !important; color: var(--text-hint) !important;
}
div[data-testid="stTextInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-ring) !important; outline: none !important;
}

/* ============================================================
   BUTTONS
   ============================================================ */
div[data-testid="stButton"] button,
div[data-testid="stFormSubmitButton"] button {
  min-height: 44px !important; border-radius: var(--radius-md) !important;
  font-size: 16px !important; font-weight: 640 !important; transition: all .13s ease !important;
}
div[data-testid="stButton"] button[kind="primary"],
div[data-testid="stFormSubmitButton"] button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid^="stBaseButton-primary"] {
  background: #2f506f !important; border-color: #2f506f !important; color: #ffffff !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid^="stBaseButton-primary"]:hover {
  background: #243f5d !important; border-color: #243f5d !important;
}
div[data-testid="stButton"] button:disabled,
div[data-testid="stFormSubmitButton"] button:disabled {
  background: #e5e7eb !important; border-color: #e5e7eb !important; color: #94a3b8 !important;
}

/* ============================================================
   AHP layout elements
   ============================================================ */
.df-ahp-guide {
  border: 1px solid var(--border); border-left: 5px solid var(--accent);
  border-radius: var(--radius-lg); padding: 12px 16px; margin: 8px 0 14px 0; background: #fafbfd;
}
.df-ahp-guide-title { font-weight: 700; margin-bottom: 6px; font-size: 16px; }
.df-ahp-guide ul { margin: 5px 0 0 1.1rem; padding: 0; }
.df-ahp-guide li { margin: 2px 0; line-height: 1.35; font-size: 15.5px; }
.df-ahp-group-title {
  text-align: left; background: #f8fafc; color: var(--text-main);
  border: 1px solid var(--border); border-left: 4px solid var(--accent);
  border-radius: var(--radius-md); padding: 8px 14px; margin: 12px 0 7px 0;
  font-weight: 750; font-size: 16px; letter-spacing: 0.01em;
}
.df-ahp-title {
  display: flex; align-items: center; justify-content: center;
  gap: 10px; font-weight: 720; font-size: 18px; margin-bottom: 7px; color: var(--text-main);
}
.df-ahp-title .vs { color: var(--text-hint); font-size: 15px; font-weight: 700; text-transform: uppercase; }
.df-ahp-scale-caption {
  display: flex; justify-content: space-between;
  color: var(--text-muted); font-size: 14px; font-weight: 600; margin: 2px 4px 5px 4px;
}
.df-ahp-layout-title { font-size: 18px; font-weight: 700; margin: 2px 0 8px 0; color: var(--text-main); }
.df-domain-desc-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 7px; }
.df-domain-desc {
  border: 1px solid var(--border); border-radius: var(--radius-md);
  background: var(--surface-soft); padding: 8px 10px; min-height: 64px;
  font-size: 15px; line-height: 1.32; color: var(--text-body);
}
.df-domain-desc-title { color: var(--text-main); font-weight: 680; margin-bottom: 4px; }
.df-domain-question {
  margin-top: 6px; padding-top: 5px; border-top: 1px solid var(--border);
  color: var(--text-main); font-weight: 600; font-size: 15px;
}
.df-domain-question.df-domain-question-top {
  margin-top: 0; padding-top: 0; padding-bottom: 6px; border-top: 0; border-bottom: 1px solid var(--border);
}
.df-domain-desc-body {
  margin-top: 6px; color: var(--text-body);
}
.df-weight-panel { border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 12px 14px; background: var(--surface); }

/* Fixed AHP result panel + quiet pedestal input
   Streamlit column wrappers often break position: sticky through overflow/transform.
   Use fixed positioning on desktop so the calibration result remains visible while scrolling. */

div[data-testid="column"]:has(.st-key-ahp_result_sticky) {
  position: relative !important;
  align-self: flex-start !important;
  min-height: 1px !important;
  overflow: visible !important;
}
div[data-testid="stVerticalBlock"]:has(.st-key-ahp_result_sticky),
div[data-testid="stHorizontalBlock"]:has(.st-key-ahp_result_sticky) {
  overflow: visible !important;
}

.st-key-ahp_result_sticky {
  position: fixed !important;
  top: 76px !important;
  right: 28px !important;
  width: clamp(320px, 23vw, 390px) !important;
  z-index: 120 !important;
  max-height: calc(100vh - 96px) !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 12px 14px 14px 14px !important;
  box-shadow: 0 8px 28px rgba(15,23,42,0.10) !important;
}

@media (max-width: 1280px) {
  .st-key-ahp_result_sticky {
    position: static !important;
    width: auto !important;
    max-height: none !important;
    overflow: visible !important;
    box-shadow: var(--shadow-card) !important;
  }
}
.st-key-ahp_result_sticky .df-ahp-layout-title { margin-top: 0 !important; }
.st-key-ahp_result_sticky div[data-testid="stTextInput"] {
  padding-bottom: 0 !important;
  min-width: 36px !important;
}
.st-key-ahp_result_sticky div[data-testid="stTextInput"] input {
  min-height: 28px !important;
  height: 28px !important;
  width: 36px !important;
  max-width: 36px !important;
  border-radius: 9px !important;
  font-size: 14px !important;
  font-weight: 650 !important;
  color: var(--text-muted) !important;
  padding: 2px 4px !important;
  text-align: center !important;
  background: #f8fafc !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
}
.st-key-ahp_result_sticky div[data-testid="stTextInput"] input:focus {
  border-color: var(--border-strong) !important;
  box-shadow: 0 0 0 2px rgba(30,58,95,0.08) !important;
}
.st-key-ahp_result_sticky div[data-testid="stTextInput"] input::placeholder {
  color: transparent !important;
}
.df-pedestal-error { display: none !important; }
.df-weight-meter { margin: 7px 0 9px 0; }
.df-weight-meter-label { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 4px; font-size: 15px; color: var(--text-body); }
.df-weight-meter-label b { font-size: 16px; font-weight: 720; color: var(--text-main); }
.df-weight-track { height: 6px; background: var(--border); border-radius: 999px; overflow: hidden; }
.df-weight-fill  { height: 100%; background: var(--accent); border-radius: 999px; }
.df-cr-card { border-radius: var(--radius-lg); padding: 10px 12px; margin: 10px 0 2px 0; border: 1px solid var(--border); background: var(--surface); }
.df-cr-card.good { background: var(--green-bg); border-color: var(--green-border); }
.df-cr-card.warn { background: var(--amber-bg); border-color: var(--amber-border); }
.df-cr-card .cr  { font-size: 1.25rem; font-weight: 800; line-height: 1; margin-bottom: 4px; }
.df-cr-card .caption { color: var(--text-body); font-size: 15px; }

/* ============================================================
   RISK CHECKLIST + REVIEW PROTOCOL
   ============================================================ */
.df-risk-status-bar {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: 10px 14px; margin: 8px 0 14px 0; background: var(--surface);
  box-shadow: var(--shadow-card); font-size: 15px; color: var(--text-body);
}
.df-risk-status-bar.good { background: var(--green-bg); border-color: var(--green-border); color: var(--green-text); }
.df-risk-status-bar.warn { background: var(--amber-bg); border-color: var(--amber-border); color: var(--amber-text); }
.df-risk-status-main { font-weight: 740; color: var(--text-main); }
.df-risk-status-bar.good .df-risk-status-main { color: var(--green-text); }
.df-risk-status-bar.warn .df-risk-status-main { color: var(--amber-text); }
.df-risk-status-meta { font-size: 14px; opacity: .9; text-align: right; }
.df-risk-group-note { color: var(--text-muted); font-size: 15px; line-height: 1.38; margin: -2px 0 8px 0; }
.df-risk-row-meta { padding: 2px 0 7px 0; border-bottom: 1px solid var(--border); }
.df-risk-row-meta:last-child { border-bottom: 0; }
.df-risk-desc { color: var(--text-body); font-size: 15px; line-height: 1.35; padding-top: 4px; }
.df-risk-signal { color: var(--amber-text); font-size: 14px; font-weight: 650; padding-top: 4px; }
.df-risk-badge {
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 999px; padding: 4px 9px; font-size: 13px; font-weight: 760;
  white-space: nowrap; border: 1px solid var(--border); background: var(--surface-soft); color: var(--text-muted);
}
.df-risk-badge.hard { background: var(--red-bg); border-color: var(--red-border); color: var(--red-text); }
.df-risk-badge.review { background: var(--amber-bg); border-color: var(--amber-border); color: var(--amber-text); }
.df-risk-badge.behavior { background: #eef6ff; border-color: #bfdbfe; color: #1d4ed8; }
.df-review-table { width: 100%; border-collapse: separate; border-spacing: 0; margin: 12px 0 20px 0; border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; background: var(--surface); }
.df-review-table th { background: var(--text-main); color: white; text-align: left; padding: 11px 14px; font-size: 15px; font-weight: 680; }
.df-review-table td { border-top: 1px solid var(--border); padding: 11px 14px; vertical-align: top; line-height: 1.4; font-size: 15px; color: var(--text-body); background: var(--surface); }
.df-review-table td:first-child { font-weight: 700; white-space: nowrap; color: var(--text-main); }
@media (max-width: 760px) {
  .df-risk-status-bar { align-items: flex-start; flex-direction: column; }
  .df-risk-status-meta { text-align: left; }
}



/* --- Intro / content pages --------------------------------- */
.df-intro-layout {
  display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px; align-items: stretch; margin: 6px 0 14px 0;
}
.df-intro-card {
  position: relative; overflow: hidden;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-xl); padding: 20px 22px 18px 22px;
  box-shadow: var(--shadow-card); height: 100%; min-height: 178px;
}
.df-intro-card::before {
  content: ""; position: absolute; left: 0; top: 0; right: 0; height: 4px;
  background: linear-gradient(90deg, var(--accent) 0%, rgba(30,58,95,0.55) 48%, var(--border-strong) 100%);
}
.df-intro-card.df-intro-note { border-left: 1px solid var(--border); }
.df-intro-card h3 { margin: 0 0 10px 0; color: var(--text-main); font-size: 19px; font-weight: 760; letter-spacing: -0.01em; }
.df-intro-card p { margin: 0 0 9px 0; color: var(--text-body); font-size: 16px; line-height: 1.48; }
.df-intro-card p:last-child { margin-bottom: 0; }
.df-intro-card ul { margin: 7px 0 0 1.15rem; padding: 0; }
.df-intro-card li { margin: 5px 0; color: var(--text-body); font-size: 16px; line-height: 1.42; }
.df-outcome-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-xl); padding: 16px 20px;
  box-shadow: var(--shadow-card); margin: 0 0 14px 0;
}
.df-outcome-title { color: var(--text-main); font-size: 18px; font-weight: 760; margin-bottom: 10px; }
.df-outcome-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
.df-outcome-chip {
  min-height: 58px; display: flex; align-items: center; justify-content: center;
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  background: var(--surface-soft); color: var(--text-main);
  font-size: 15.5px; font-weight: 680; text-align: center; padding: 9px 12px;
}
.df-stepper-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-xl); padding: 15px 18px;
  box-shadow: var(--shadow-card); margin: 0 0 12px 0;
}
.df-stepper-title { color: var(--text-main); font-size: 18px; font-weight: 760; margin-bottom: 11px; }
.df-stepper { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; }
.df-stepper-step {
  border: 1px solid var(--border); border-radius: var(--radius-md);
  background: var(--surface-soft); padding: 9px 8px;
  min-height: 54px; display: flex; align-items: center; gap: 8px;
}
.df-stepper-num {
  width: 24px; height: 24px; border-radius: 999px; flex: 0 0 24px;
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--accent); color: #fff; font-size: 13px; font-weight: 780;
}
.df-stepper-label { color: var(--text-body); font-size: 14.5px; line-height: 1.15; font-weight: 650; }
.st-key-welcome_cta div[data-testid="stButton"] button {
  min-height: 52px !important; font-size: 17px !important; font-weight: 720 !important;
  border-radius: var(--radius-lg) !important;
}
@media (max-width: 1180px) { .df-stepper { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 980px) { .df-intro-layout { grid-template-columns: 1fr; } .df-outcome-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) { .df-stepper, .df-outcome-grid { grid-template-columns: 1fr; } }

/* ============================================================
   COMPACT DECISION DASHBOARD
   ============================================================ */
.df-dash-section { margin: 14px 0 18px 0; }
.df-dash-section-title {
  font-size: 17px; font-weight: 760; color: var(--text-main);
  margin: 14px 0 8px 0; letter-spacing: -0.01em;
}
.df-dashboard-grid {
  display: grid; grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px; margin: 8px 0 12px 0; align-items: stretch;
}
.df-dashboard-kpi {
  min-height: 76px; height: 100%; border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 12px 13px;
  background: var(--surface); box-shadow: var(--shadow-card);
  display: flex; flex-direction: column; justify-content: space-between;
}
.df-dashboard-kpi .kpi-label {
  color: var(--text-muted); font-size: 13.5px; font-weight: 650;
  text-transform: uppercase; letter-spacing: .025em;
}
.df-dashboard-kpi .kpi-value {
  color: var(--text-main); font-size: 24px; line-height: 1.05;
  font-weight: 820; letter-spacing: -0.03em; margin-top: 5px;
  word-break: break-word;
}
.df-dashboard-kpi .kpi-note { color: var(--text-muted); font-size: 14px; line-height: 1.25; margin-top: 5px; }
.df-dashboard-kpi.good { border-color: var(--green-border); background: var(--green-bg); }
.df-dashboard-kpi.warn { border-color: var(--amber-border); background: var(--amber-bg); }
.df-dashboard-kpi.bad  { border-color: var(--red-border); background: var(--red-bg); }
.df-dashboard-kpi.good .kpi-value { color: var(--green-text); }
.df-dashboard-kpi.warn .kpi-value { color: var(--amber-text); }
.df-dashboard-kpi.bad .kpi-value  { color: var(--red-text); }
.df-recommendation-panel {
  border: 1px solid var(--border); border-left: 5px solid var(--accent);
  border-radius: var(--radius-lg); background: var(--surface);
  padding: 13px 16px; margin: 10px 0 12px 0; box-shadow: var(--shadow-card);
}
.df-recommendation-panel.good { border-left-color: var(--green-text); }
.df-recommendation-panel.warn { border-left-color: var(--amber-text); }
.df-recommendation-panel.bad  { border-left-color: var(--red-text); }
.df-recommendation-title { font-size: 16px; font-weight: 780; color: var(--text-main); margin-bottom: 3px; }
.df-recommendation-body { font-size: 15px; color: var(--text-body); line-height: 1.42; }
.df-score-table, .df-domain-table, .df-governance-table {
  width: 100%; border-collapse: separate; border-spacing: 0;
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  overflow: hidden; background: var(--surface); box-shadow: var(--shadow-card);
  margin: 8px 0 12px 0;
}
.df-score-table th, .df-domain-table th, .df-governance-table th {
  background: #f8fafc; color: var(--text-muted); text-align: left;
  font-size: 13.5px; font-weight: 760; text-transform: uppercase;
  letter-spacing: .025em; padding: 8px 10px; border-bottom: 1px solid var(--border);
}
.df-score-table td, .df-domain-table td, .df-governance-table td {
  padding: 8px 10px; border-bottom: 1px solid var(--border);
  font-size: 15px; color: var(--text-body); vertical-align: middle; line-height: 1.32;
}
.df-score-table tr:last-child td, .df-domain-table tr:last-child td, .df-governance-table tr:last-child td { border-bottom: 0; }
.df-score-table .sum-row td { background: #f8fafc; color: var(--text-main); font-weight: 780; }
.df-mini-bar { height: 7px; background: #e5e7eb; border-radius: 999px; overflow: hidden; min-width: 84px; }
.df-mini-bar-fill { height: 100%; border-radius: 999px; background: var(--accent); }
.df-domain-chip, .df-risk-chip {
  display: inline-flex; align-items: center; padding: 3px 7px;
  border-radius: 999px; border: 1px solid var(--border);
  background: var(--surface-soft); color: var(--text-muted);
  font-size: 13.5px; font-weight: 650; margin: 1px 3px 1px 0;
}
.df-risk-chip.good { border-color: var(--green-border); color: var(--green-text); background: var(--green-bg); }
.df-risk-chip.warn { border-color: var(--amber-border); color: var(--amber-text); background: var(--amber-bg); }
.df-risk-chip.bad  { border-color: var(--red-border); color: var(--red-text); background: var(--red-bg); }
.df-domain-card-compact {
  border: 1px solid var(--border); border-radius: var(--radius-lg); background: var(--surface);
  padding: 12px 14px; min-height: 96px; height: 100%; box-shadow: var(--shadow-card);
}
.df-domain-card-compact .title { color: var(--text-muted); font-size: 14px; font-weight: 720; text-transform: uppercase; letter-spacing: .025em; }
.df-domain-card-compact .score { color: var(--text-main); font-size: 26px; font-weight: 820; line-height: 1.08; margin: 4px 0; }
.df-domain-card-compact .body { color: var(--text-body); font-size: 14.5px; line-height: 1.35; }
.df-sub-table-wrap { overflow-x: auto; margin: 4px 0 8px 0; }
.df-muted { color: var(--text-muted); }
@media (max-width: 1180px) { .df-dashboard-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 760px) { .df-dashboard-grid { grid-template-columns: 1fr; } }

/* misc */
.df-step { color: var(--accent); font-weight: 700; letter-spacing: 0.02em; text-transform: uppercase; font-size: 13px; }
hr { margin: 1rem 0; border-color: var(--border); }


/* ============================================================
   DEPLOY THEME HARDENING — force full light UI on Streamlit Cloud
   Must stay at the end of the main CSS block to override Streamlit
   dark-theme tokens and broad text rules.
   ============================================================ */
html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section.main,
main {
  background: var(--bg) !important;
  color: var(--text-body) !important;
}

[data-testid="stHeader"] {
  background: #0b1118 !important;
}

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {
  background: #f8fafc !important;
  color: var(--text-body) !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
  color: var(--text-body) !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: var(--text-main) !important;
}
[data-testid="stSidebar"] hr {
  border-color: var(--border) !important;
}

/* Native Streamlit buttons: parent + all internal markdown wrappers. */
div[data-testid="stButton"] button,
div[data-testid="stFormSubmitButton"] button,
div[data-testid="stDownloadButton"] button,
button[data-testid^="stBaseButton"] {
  background: var(--surface) !important;
  border: 1px solid var(--border-strong) !important;
  color: var(--accent) !important;
  opacity: 1 !important;
  box-shadow: none !important;
}
div[data-testid="stButton"] button *,
div[data-testid="stFormSubmitButton"] button *,
div[data-testid="stDownloadButton"] button *,
button[data-testid^="stBaseButton"] *,
div[data-testid="stButton"] button p,
div[data-testid="stFormSubmitButton"] button p,
div[data-testid="stDownloadButton"] button p,
button[data-testid^="stBaseButton"] p {
  color: inherit !important;
}
div[data-testid="stButton"] button:hover,
div[data-testid="stFormSubmitButton"] button:hover,
div[data-testid="stDownloadButton"] button:hover,
button[data-testid^="stBaseButton"]:hover {
  background: #f3f7fc !important;
  border-color: var(--accent) !important;
  color: var(--accent) !important;
}
div[data-testid="stButton"] button[kind="primary"],
div[data-testid="stFormSubmitButton"] button[kind="primary"],
div[data-testid="stDownloadButton"] button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid^="stBaseButton-primary"] {
  background: #2f506f !important;
  border-color: #2f506f !important;
  color: #ffffff !important;
}
div[data-testid="stButton"] button[kind="primary"] *,
div[data-testid="stFormSubmitButton"] button[kind="primary"] *,
div[data-testid="stDownloadButton"] button[kind="primary"] *,
button[data-testid="stBaseButton-primary"] *,
button[data-testid^="stBaseButton-primary"] * {
  color: #ffffff !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
div[data-testid="stDownloadButton"] button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid^="stBaseButton-primary"]:hover {
  background: #243f5d !important;
  border-color: #243f5d !important;
  color: #ffffff !important;
}
div[data-testid="stButton"] button:disabled,
div[data-testid="stButton"] button[disabled],
div[data-testid="stButton"] button[aria-disabled="true"],
div[data-testid="stFormSubmitButton"] button:disabled,
div[data-testid="stFormSubmitButton"] button[disabled],
div[data-testid="stFormSubmitButton"] button[aria-disabled="true"],
button[data-testid^="stBaseButton"]:disabled,
button[data-testid^="stBaseButton"][disabled],
button[data-testid^="stBaseButton"][aria-disabled="true"] {
  background: #e5e7eb !important;
  border-color: #e5e7eb !important;
  color: #64748b !important;
  opacity: 1 !important;
  cursor: not-allowed !important;
}
div[data-testid="stButton"] button:disabled *,
div[data-testid="stButton"] button[disabled] *,
div[data-testid="stButton"] button[aria-disabled="true"] *,
div[data-testid="stFormSubmitButton"] button:disabled *,
div[data-testid="stFormSubmitButton"] button[disabled] *,
div[data-testid="stFormSubmitButton"] button[aria-disabled="true"] *,
button[data-testid^="stBaseButton"]:disabled *,
button[data-testid^="stBaseButton"][disabled] *,
button[data-testid^="stBaseButton"][aria-disabled="true"] * {
  color: #64748b !important;
}

/* Sidebar navigation buttons need separate contrast rules. */
[data-testid="stSidebar"] div[data-testid="stButton"] button {
  background: #ffffff !important;
  border: 1px solid #cbd5e1 !important;
  color: var(--accent) !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] button *,
[data-testid="stSidebar"] div[data-testid="stButton"] button p,
[data-testid="stSidebar"] div[data-testid="stButton"] button span {
  color: var(--accent) !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
  background: #eef6ff !important;
  border-color: var(--accent) !important;
}

/* Radio cards / expanders / tables: override inherited dark Streamlit tokens. */
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] label *,
div[data-testid="stRadio"] label p,
div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] label *,
div[data-testid="stCheckbox"] label p,
div[data-testid="stExpander"] *,
div[data-testid="stDataFrame"] *,
table,
table * {
  color: var(--text-body) !important;
}
div[data-testid="stRadio"] label p:first-of-type,
div[data-testid="stExpander"] details summary,
div[data-testid="stExpander"] details summary *,
th,
th * {
  color: var(--text-main) !important;
}
.df-review-table th,
.df-review-table th * {
  color: #ffffff !important;
}
.df-review-table td,
.df-review-table td * {
  color: var(--text-body) !important;
}
.df-review-table td:first-child,
.df-review-table td:first-child * {
  color: var(--text-main) !important;
}

/* Custom HTML cards must not be affected by dark parent containers. */
.df-card,
.df-intro-card,
.df-outcome-card,
.df-stepper-card,
.df-prem-domain-card,
.df-domain-card-compact,
.df-dashboard-kpi,
.df-recommendation-panel,
.df-risk-status-bar,
.df-review-table,
.df-score-table,
.df-domain-table,
.df-governance-table {
  color: var(--text-body) !important;
}
.df-card *,
.df-intro-card *,
.df-outcome-card *,
.df-stepper-card *,
.df-prem-domain-card *,
.df-domain-card-compact *,
.df-dashboard-kpi *,
.df-recommendation-panel *,
.df-risk-status-bar *,
.df-review-table *,
.df-score-table *,
.df-domain-table *,
.df-governance-table * {
  color: inherit;
}
.df-prem-title,
.df-prem-title *,
.df-intro-card h3,
.df-outcome-title,
.df-stepper-title,
.df-domain-card-compact .score,
.df-dashboard-kpi .kpi-value,
.df-recommendation-title,
.df-risk-status-main,
.df-stepper-label,
.df-outcome-chip,
.df-domain-desc-title {
  color: var(--text-main) !important;
}
.df-prem-meta,
.df-prem-domain-subtitle,
.df-intro-card p,
.df-intro-card li,
.df-dashboard-kpi .kpi-note,
.df-recommendation-body,
.df-domain-card-compact .body,
.df-stepper-label {
  color: var(--text-body) !important;
}

/* AHP choice buttons have their own forced readability. */
div[class*="st-key-ahp_choice_"] div[data-testid="stButton"] button,
div[class*="st-key-ahp_choice_"] div[data-testid="stButton"] button *,
div[class*="st-key-ahp_choice_"] div[data-testid="stButton"] button p,
div[class*="st-key-ahp_choice_"] div[data-testid="stButton"] button span {
  background: var(--surface) !important;
  color: var(--text-body) !important;
}

</style>
"""


def init_state() -> None:
    """Initialize Streamlit session state with stable defaults."""
    defaults = {
        "current_step": "welcome",
        "mcda_index": 0,
        "case_data": {
            "title": "",
            "context": "",
            "dilemma": "",
            "options": ["", "", "", ""],
            "type": "operating business",
            "amount": 0.0,
            "currency": "USD",
            "horizon": "3–12 місяців",
            "emotion": "calm",
        },
        "ahp_answers": {pid: 1.0 for pid, _, _ in PAIRWISE},
        "ahp_revealed_pairs": [AHP_FIRST_PAIR],
        "ahp_answered_pairs": [],
        "portfolio_basket": None,
        "ahp_matrix": None,
        "ahp_weights": {d["key"]: 1.0 / len(DOMAINS) for d in DOMAINS},
        "consistency_ratio": 0.0,
        "consistency_warnings": [],
        "veto_answers": {v["key"]: False for v in VETO_ITEMS},
        "veto_notes": {v["key"]: "" for v in VETO_ITEMS},
        "mcda_answers": default_mcda_answers(),
        "mcda_notes": {c["key"]: "" for c in CRITERIA},
        "domain_scores": {},
        "final_score": None,
        "decision_status": "",
        "governance_warnings": [],
        "memo_markdown": "",
        "counterargument": "",
        "ahp_baseline_hint_seen": False,
        "scroll_to_top": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Legacy cleanup: previous versions stored IRR as a numeric benefit dict.
    # IRR is now a 0/3/5/7/10 scale criterion, so old dict payloads must be cleared.
    irr_answer = st.session_state.get("mcda_answers", {}).get("irr")
    if isinstance(irr_answer, dict):
        st.session_state["mcda_answers"]["irr"] = None
    for legacy_key in ("num_irr_min", "num_irr_value", "num_irr_max"):
        if legacy_key in st.session_state:
            del st.session_state[legacy_key]


def reset_decision_state(target_step: str = PAGE_AHP) -> None:
    """Clear all user inputs and widget state, then start a fresh decision."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()
    st.session_state.current_step = target_step
    st.session_state.mcda_index = 0
    st.session_state.scroll_to_top = True
    calculate_ahp()
    st.rerun()


def default_mcda_answers() -> dict[str, Any]:
    """Build empty MCDA answer structure from criterion definitions."""
    answers = {}
    for c in CRITERIA:
        if c["type"] == "scale":
            answers[c["key"]] = None
        elif c["type"] == "benefit":
            answers[c["key"]] = dict(c["default"])
        elif c["type"] == "cost":
            answers[c["key"]] = dict(c["default"])
    return answers


def go(step: str, mcda_index: int | None = None) -> None:
    """Navigate to another wizard step and rerun Streamlit."""
    previous_step = st.session_state.get("current_step")
    previous_mcda_index = st.session_state.get("mcda_index")

    st.session_state.current_step = step
    if mcda_index is not None:
        limit = len(DOMAINS) - 1 if step == "mcda" else len(CRITERIA) - 1
        st.session_state.mcda_index = max(0, min(limit, mcda_index))

    # Streamlit keeps the browser scroll position between reruns.
    # Force top-of-page only for real navigation/page changes, not for ordinary widget reruns.
    if previous_step != step or previous_mcda_index != st.session_state.get("mcda_index"):
        st.session_state.scroll_to_top = True
    st.rerun()


def safe_float(value: Any, fallback: float = 0.0) -> float:
    """Convert a value to float; return fallback on empty or invalid input."""
    try:
        if value is None or value == "":
            return fallback
        return float(value)
    except (TypeError, ValueError):
        return fallback



def parse_optional_int(value: Any) -> int | None:
    """Parse a non-negative integer-like input; return None for invalid or empty values."""
    raw = str(value).strip().replace(" ", "")
    if raw == "" or raw.lower() == "none":
        return None
    if raw.startswith("+"):
        raw = raw[1:]
    if raw.startswith("-"):
        return None
    if not raw.isdigit():
        return None
    return int(raw)


def parse_int_input(value: Any, fallback: int = 0) -> int:
    """Parse integer input with a fallback."""
    parsed = parse_optional_int(value)
    return int(fallback) if parsed is None else int(parsed)

def clamp01(value: float) -> float:
    """Clamp a numeric value to the 0..1 range."""
    return max(0.0, min(1.0, float(value)))


def pair_option_index(value: float) -> int:
    values = [v for _, v in PAIRWISE_OPTIONS]
    return min(range(len(values)), key=lambda i: abs(values[i] - float(value)))


def pair_option_label(left: str, right: str, label: str) -> str:
    # Internal labels are intentionally short in the UI; direction is shown by position.
    return AHP_OPTION_LABELS.get(label, str(label))


def radio_index_from_value(options: Sequence[Any], value: Any) -> int | None:
    if value is None or value not in options:
        return None
    return options.index(value)


def basket_option_label(bkey: str) -> str:
    cfg = BASKET_CONFIG[bkey]
    return cfg["label"] + "\n\n" + cfg["description"]


def criteria_for_domain(domain_key: str) -> list[CriterionConfig]:
    """Return MCDA criteria belonging to one domain."""
    return [c for c in CRITERIA if c["domain"] == domain_key]


def mcda_domain_index() -> int:
    """Return a safe current MCDA domain index from session state."""
    try:
        idx = int(st.session_state.get("mcda_index", 0) or 0)
    except (TypeError, ValueError):
        idx = 0
    return max(0, min(len(DOMAINS) - 1, idx))


def scale_anchor_label(c: Mapping[str, Any], value: int) -> str:
    # Keep the exact anchor text in one typographic level.
    # This avoids optical imbalance where only some cards get a separate subtext line.
    raw = str(c.get("anchors", {}).get(str(value), str(value))).strip()
    return raw if raw else str(value)


def scale_anchor_index(c: Mapping[str, Any]) -> int:
    anchors = SCALE_ANCHORS
    current = st.session_state.mcda_answers.get(c["key"])
    if current is None:
        return None
    try:
        current_value = float(current)
    except (TypeError, ValueError):
        return None
    return min(range(len(anchors)), key=lambda n: abs(anchors[n] - current_value))


MCDA_DOMAIN_SUMMARIES = {
    "economic_quality": "Оціни економічну якість об’єкта: фінансову віддачу, cash flow, ліквідність і захист від втрат.",
    "strategic_significance": "Оціни, наскільки об’єкт посилює твою майбутню позицію: нові ходи, навички, системи й ринкову силу.",
    "asset_controllability": "Оціни, наскільки ти реально впливаєш на результат: команда, прозорість, governance і права змінювати курс.",
    "management_load": "Оціни ціну об’єкта для часу, уваги, фокусу й перемикання контекстів.",
    "personal_fit": "Оціни, наскільки об’єкт сумісний із мотивацією, стресом, відновленням, цінностями й self-respect.",
}


def mcda_domain_summary(domain_key: str) -> str:
    """Return short explanatory text for an MCDA domain."""
    return MCDA_DOMAIN_SUMMARIES.get(domain_key, "Оціни критерії цього домену.")


def calculate_ahp() -> tuple[np.ndarray, ScoreMap, float, list[dict[str, Any]]]:
    """Calculate AHP matrix, domain weights and consistency diagnostics."""
    n = len(DOMAINS)
    idx = {d["key"]: i for i, d in enumerate(DOMAINS)}
    matrix = np.ones((n, n), dtype=float)

    for pid, left, right in PAIRWISE:
        val = float(st.session_state.ahp_answers.get(pid, 1.0))
        i, j = idx[left], idx[right]
        matrix[i, j] = val
        matrix[j, i] = 1.0 / val

    eigvals, eigvecs = np.linalg.eig(matrix)
    max_idx = int(np.argmax(eigvals.real))
    lambda_max = float(eigvals[max_idx].real)
    weights_raw = np.abs(eigvecs[:, max_idx].real)
    weights = weights_raw / weights_raw.sum()

    ri = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    cr = 0.0 if ri[n] == 0 else ci / ri[n]

    weight_dict = {DOMAINS[i]["key"]: float(weights[i]) for i in range(n)}
    warnings = detect_consistency_conflicts(matrix)

    st.session_state.ahp_matrix = matrix.tolist()
    st.session_state.ahp_weights = weight_dict
    st.session_state.consistency_ratio = float(max(0.0, cr))
    st.session_state.consistency_warnings = warnings
    return matrix, weight_dict, max(0.0, cr), warnings


def detect_consistency_conflicts(matrix: np.ndarray) -> list[dict[str, Any]]:
    warnings = []
    idx = {d["key"]: i for i, d in enumerate(DOMAINS)}
    for a, b, c in combinations([d["key"] for d in DOMAINS], 3):
        i, j, k = idx[a], idx[b], idx[c]
        expected = matrix[i, j] * matrix[j, k]
        actual = matrix[i, k]
        if expected <= 0 or actual <= 0:
            continue
        conflict_score = abs(math.log(expected) - math.log(actual))
        pair_ids = [
            PAIR_BY_SET[frozenset((a, b))],
            PAIR_BY_SET[frozenset((b, c))],
            PAIR_BY_SET[frozenset((a, c))],
        ]
        warnings.append({
            "triad": [a, b, c],
            "pair_ids": pair_ids,
            "expected": float(expected),
            "actual": float(actual),
            "conflict_score": float(conflict_score),
        })
    warnings.sort(key=lambda x: x["conflict_score"], reverse=True)
    return warnings[:3]


def ahp_pattern_hints() -> list[str]:
    values = list(st.session_state.ahp_answers.values())
    extremes = sum(1 for v in values if v >= 7 or v <= 1 / 7)
    equals = sum(1 for v in values if abs(v - 1) < 1e-9)
    hints = []
    if extremes >= 3:
        hints.append("У матриці багато крайніх оцінок. 7 і 9 варто використовувати лише тоді, коли один домен майже завжди важливіший за інший. Спробуй пом’якшити частину оцінок до 3 або 5.")
    if equals >= 6 and extremes >= 1:
        hints.append("Більшість доменів близькі за важливістю, але є різка перевага в одній парі. Перевір, чи це справді принципова різниця, а не реакція на поточний кейс.")
    if st.session_state.case_data.get("emotion") in {"overloaded", "stressed", "tired", "excited"}:
        hints.append("Поточний стан може підміняти стратегічну вагу. Порівнюй не те, що зараз болить найбільше, а те, що має бути важливим для якісного рішення в нормальному стані.")
    return hints[:3]


def ahp_valid_pair_ids() -> set[str]:
    return {pid for pid, _, _ in PAIRWISE}


def ahp_revealed_pairs() -> list[str]:
    valid = ahp_valid_pair_ids()
    revealed = st.session_state.get("ahp_revealed_pairs")
    if not isinstance(revealed, list):
        revealed = [AHP_FIRST_PAIR]
    cleaned = []
    for pid in revealed:
        if pid in valid and pid not in cleaned:
            cleaned.append(pid)
    if not cleaned:
        cleaned = [AHP_FIRST_PAIR]
    st.session_state.ahp_revealed_pairs = cleaned
    return cleaned


def ahp_answered_pairs() -> set[str]:
    valid = ahp_valid_pair_ids()
    answered = st.session_state.get("ahp_answered_pairs")
    if not isinstance(answered, list):
        answered = []
    cleaned = []
    for pid in answered:
        if pid in valid and pid not in cleaned:
            cleaned.append(pid)
    st.session_state.ahp_answered_pairs = cleaned
    return cleaned


def set_ahp_pair_answer(pid: str, option_idx: int) -> None:
    """Set one AHP answer directly from a clicked option button."""
    if pid not in ahp_valid_pair_ids():
        return
    try:
        idx = int(option_idx)
    except (TypeError, ValueError):
        return
    if not 0 <= idx < len(PAIRWISE_OPTIONS):
        return
    st.session_state.ahp_answers[pid] = PAIRWISE_OPTIONS[idx][1]
    answered = ahp_answered_pairs()
    if pid not in answered:
        answered.append(pid)
        st.session_state.ahp_answered_pairs = answered
    advance_ahp_flow_from(pid)


def sync_ahp_answer_from_widget(pid: str) -> None:
    """Legacy no-op: AHP no longer reads duplicate-label radio widgets."""
    return False


def sync_ahp_answers_from_widgets() -> None:
    """Keep dynamic AHP flow valid without reading stale radio widget state."""
    ensure_ahp_flow_state()


def ahp_winner_counts() -> dict[str, int]:
    counts = {d["key"]: 0.0 for d in DOMAINS}
    for pid in ahp_answered_pairs():
        left, right = PAIR_LOOKUP[pid]
        value = float(st.session_state.ahp_answers.get(pid, 1.0))
        if value > 1.0:
            counts[left] += abs(math.log(value))
        elif value < 1.0:
            counts[right] += abs(math.log(1.0 / value))
    return counts


def choose_next_ahp_pair(last_pid: str | None) -> str | None:
    revealed = ahp_revealed_pairs()
    answered = ahp_answered_pairs()
    candidates = [pid for pid in AHP_BASE_SEQUENCE if pid not in revealed]
    if not candidates:
        return None

    left, right = PAIR_LOOKUP[last_pid]
    value = float(st.session_state.ahp_answers.get(last_pid, 1.0))

    if value > 1.0:
        winner = left
        winner_candidates = [pid for pid in candidates if winner in PAIR_LOOKUP[pid]]
        if winner_candidates:
            return winner_candidates[0]
    elif value < 1.0:
        winner = right
        winner_candidates = [pid for pid in candidates if winner in PAIR_LOOKUP[pid]]
        if winner_candidates:
            return winner_candidates[0]
    else:
        neutral_candidates = [pid for pid in candidates if left not in PAIR_LOOKUP[pid] and right not in PAIR_LOOKUP[pid]]
        if neutral_candidates:
            return neutral_candidates[0]

    counts = ahp_winner_counts()
    base_index = {pid: i for i, pid in enumerate(AHP_BASE_SEQUENCE)}
    return max(
        candidates,
        key=lambda pid: (
            counts.get(PAIR_LOOKUP[pid][0], 0.0) + counts.get(PAIR_LOOKUP[pid][1], 0.0),
            max(counts.get(PAIR_LOOKUP[pid][0], 0.0), counts.get(PAIR_LOOKUP[pid][1], 0.0)),
            -base_index.get(pid, 999),
        ),
    )


def advance_ahp_flow_from(pid: str) -> None:
    revealed = ahp_revealed_pairs()
    answered = ahp_answered_pairs()
    if pid not in answered:
        return
    if not revealed or revealed[-1] != pid:
        return
    next_pid = choose_next_ahp_pair(pid)
    if next_pid and next_pid not in revealed:
        revealed.append(next_pid)
        st.session_state.ahp_revealed_pairs = revealed


def ensure_ahp_flow_state() -> None:
    revealed = ahp_revealed_pairs()
    answered = ahp_answered_pairs()
    while revealed and revealed[-1] in answered and len(revealed) < len(PAIRWISE):
        next_pid = choose_next_ahp_pair(revealed[-1])
        if not next_pid or next_pid in revealed:
            break
        revealed.append(next_pid)
        st.session_state.ahp_revealed_pairs = revealed


def handle_ahp_radio_change(pid: str) -> None:
    """Legacy callback retained for old sessions; no longer used by AHP buttons."""
    return None


def ahp_pair_radio_index(pid: str) -> int:
    widget_key = f"radio_{pid}"
    if widget_key in st.session_state and st.session_state.get(widget_key) is not None:
        try:
            idx = int(st.session_state.get(widget_key))
            if 0 <= idx < len(PAIRWISE_OPTIONS):
                return idx
        except (TypeError, ValueError):
            return None
    if pid in ahp_answered_pairs():
        return pair_option_index(st.session_state.ahp_answers.get(pid, 1.0))
    return None


def normalized_criterion_score(c: Mapping[str, Any]) -> float | None:
    answer = st.session_state.mcda_answers.get(c["key"])
    if c["type"] == "scale":
        return clamp01(safe_float(answer, 0.0) / 10.0)
    if c["type"] == "benefit":
        value = safe_float(answer.get("value"), 0.0)
        min_value = safe_float(answer.get("min"), 0.0)
        max_value = safe_float(answer.get("max"), 0.0)
        if max_value <= min_value:
            return 0.0
        return clamp01((value - min_value) / (max_value - min_value))
    if c["type"] == "cost":
        value = safe_float(answer.get("value"), 0.0)
        ideal = safe_float(answer.get("ideal"), 0.0)
        worst = safe_float(answer.get("worst"), 0.0)
        if worst <= ideal:
            return 0.0
        return clamp01((worst - value) / (worst - ideal))
    return 0.0


def calculate_scores() -> tuple[ScoreMap, ScoreMap, float, str, list[str]]:
    """Calculate domain scores, final score, status and gate warnings."""
    domain_scores = {}
    criterion_scores = {}

    for c in CRITERIA:
        score = normalized_criterion_score(c)
        criterion_scores[c["key"]] = score

    for d in DOMAINS:
        domain_criteria = [c for c in CRITERIA if c["domain"] == d["key"]]
        if domain_criteria:
            domain_scores[d["key"]] = float(np.mean([criterion_scores[c["key"]] for c in domain_criteria]) * 100)
        else:
            domain_scores[d["key"]] = 0.0

    weights = st.session_state.ahp_weights or {d["key"]: 1.0 / len(DOMAINS) for d in DOMAINS}
    final = sum(domain_scores[k] * weights.get(k, 0.0) for k in domain_scores)

    status = base_status(final)

    asset_type = st.session_state.case_data.get("type", "")
    gates = []
    governance_warnings = []

    if domain_scores.get("economic_quality", 0) < 60:
        gates.append("Фінанси < 60")

    low_controllability = domain_scores.get("asset_controllability", 0) < 60
    if low_controllability and asset_type in ACTIVE_ASSET_TYPES:
        gates.append("Керованість < 60")
    elif low_controllability:
        governance_warnings.append(
            f"Керованість < 60: governance-ризик для типу '{asset_type or 'не вказано'}'; це не доменний поріг і не знижує статус."
        )

    if gates:
        decision_status = f"{downgrade_status(status)} / GATE REVIEW"
    else:
        decision_status = status

    st.session_state.domain_scores = domain_scores
    st.session_state.final_score = float(final)
    st.session_state.decision_status = decision_status
    st.session_state.governance_warnings = governance_warnings
    return domain_scores, criterion_scores, final, decision_status, gates


def base_status(score: float, basket: str | None = None) -> str:
    b = basket or st.session_state.get("portfolio_basket") or "core"
    cfg = BASKET_CONFIG.get(b, BASKET_CONFIG["core"])
    t = cfg["thresholds"]
    if score >= t["invest"]:
        return "INVEST"
    if score >= t["hold"]:
        return "HOLD"
    if score >= t["refactor"]:
        return "REFACTOR"
    return "EXIT"


def downgrade_status(status: str) -> str:
    base = str(status).split(" /")[0]
    if base not in STATUS_ORDER:
        return "REFACTOR"
    idx = STATUS_ORDER.index(base)
    return STATUS_ORDER[min(idx + 1, len(STATUS_ORDER) - 1)]


def active_vetoes() -> list[dict[str, Any]]:
    return [v for v in VETO_ITEMS if st.session_state.veto_answers.get(v["key"], False)]


def format_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_score(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:.1f}"


def card(title: str, body: str, kind: str = "neutral") -> str:
    cls = "df-card"
    if kind == "green":
        cls += " df-green"
    elif kind == "amber":
        cls += " df-amber"
    elif kind == "red":
        cls += " df-red"
    st.markdown(f'<div class="{cls}"><h3>{title}</h3><div>{body}</div></div>', unsafe_allow_html=True)



def render_evidence_prompt(c: Mapping[str, Any]) -> None:
    st.markdown(
        f"<div class='df-card' style='padding:12px 14px; margin-top:8px; margin-bottom:12px; background:#f9fafb;'><strong>Що врахувати:</strong> <em>{escape(str(c.get('evidence', '')))}</em></div>",
        unsafe_allow_html=True,
    )


def ahp_domain_label(domain_key: str) -> str:
    return AHP_DOMAIN_COPY.get(domain_key, {}).get("label", DOMAIN_BY_KEY[domain_key]["label"])


def ahp_choice_strip_colors(left_domain: str, right_domain: str, option_key: str) -> tuple[str, str]:
    """Return left/right strip colors for one AHP choice button."""
    level = AHP_OPTION_COLOR_LEVEL.get(option_key, "light")
    transparent = "transparent"
    if option_key.startswith("left_"):
        return AHP_DOMAIN_COLORS[left_domain][level], transparent
    if option_key.startswith("right_"):
        return transparent, AHP_DOMAIN_COLORS[right_domain][level]
    return AHP_DOMAIN_COLORS[left_domain]["light"], AHP_DOMAIN_COLORS[right_domain]["light"]


def render_ahp_choice_style(choice_key: str, left_color: str, right_color: str, selected: bool) -> None:
    """Inject per-button color variables and selected styling."""
    selected_rule = ""
    if selected:
        selected_rule = f"""
        .st-key-{choice_key} div[data-testid='stButton'] button,
        .st-key-{choice_key} div[data-testid='stButton'] button:hover,
        .st-key-{choice_key} div[data-testid='stButton'] button:focus {{
          border: 3px solid var(--accent) !important;
          outline: 2px solid var(--accent) !important;
          outline-offset: -2px !important;
          background: #f3f7fc !important;
          color: var(--text-main) !important;
          font-weight: 800 !important;
          box-shadow: 0 0 0 4px var(--accent-ring) !important;
        }}
        """
    st.markdown(
        f"""
        <style>
        .st-key-{choice_key} {{ --ahp-left-strip: {left_color}; --ahp-right-strip: {right_color}; }}
        {selected_rule}
        </style>
        """,
        unsafe_allow_html=True,
    )


def domain_description_card(domain_key: str) -> str:
    copy = AHP_DOMAIN_COPY.get(domain_key, {})
    description = copy.get("description", DOMAIN_BY_KEY[domain_key].get("explain", ""))
    question = copy.get("question", DOMAIN_BY_KEY[domain_key].get("question", ""))

    safe_question = escape(str(question)) if question else ""
    safe_description = escape(str(description)).replace("\n", "<br>") if description else ""

    question_html = (
        f"<div class='df-domain-question df-domain-question-top'><strong>{safe_question}</strong></div>"
        if safe_question else ""
    )
    desc_html = (
        f"<div class='df-domain-desc-body'>{safe_description}</div>"
        if safe_description else ""
    )
    return (
        f"<div class='df-domain-desc'>"
        f"{question_html}"
        f"{desc_html}"
        f"</div>"
    )


def render_header() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def render_premium_page_header(title: str, meta: str = "", progress: float = 0.0, completion: str | None = None) -> None:
    safe_title = escape(str(title))
    safe_meta = escape(str(meta)) if meta else ""
    right = f"<div class='df-prem-completion'>{escape(str(completion))}</div>" if completion else ""
    meta_html = f"<div class='df-prem-meta'>{safe_meta}</div>" if safe_meta else ""
    progress_width = max(0.0, min(100.0, float(progress)))
    st.markdown(
        f"""
        <div class='df-prem-page-head'>
          <div>
            <div class='df-prem-title'>{safe_title}</div>
            {meta_html}
          </div>
          {right}
        </div>
        <div class='df-prem-progress'><div class='df-prem-progress-fill' style='width:{progress_width:.1f}%;'></div></div>
        """,
        unsafe_allow_html=True,
    )

def render_premium_intro_card(title: str, body: str) -> None:
    st.markdown(
        f"<div class='df-prem-domain-card'><div class='df-prem-domain-title'>{escape(str(title))}</div><div class='df-prem-domain-subtitle'>{body}</div></div>",
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    st.sidebar.title("Навігація")
    steps = [
        ("welcome", "Вступ"),
        ("ahp", "AHP"),
        ("basket", "Роль у портфелі"),
        ("veto", "Стоп-фактори"),
        ("mcda", "MCDA"),
        ("dashboard", "Панель рішення"),
        ("memo", "Мемо"),
    ]
    for key, label in steps:
        if st.sidebar.button(label, use_container_width=True, key=f"nav_{key}"):
            go(key, st.session_state.mcda_index if key == "mcda" else None)

    st.sidebar.divider()
    st.sidebar.caption("Поточний стан")
    cr = st.session_state.get("consistency_ratio", 0.0)
    st.sidebar.write(f"CR: **{cr:.3f}**")
    basket = st.session_state.get("portfolio_basket")
    st.sidebar.write(f"Кошик: **{BASKET_CONFIG[basket]['label'] if basket else '—'}**")
    st.sidebar.write(f"Stop-фактори: **{len(active_vetoes())}**")
    score = st.session_state.get("final_score")
    st.sidebar.write(f"Score: **{format_score(score)}**")


def export_draft() -> dict[str, Any]:
    """Serialize the current decision draft from session state."""
    return {
        "case_data": st.session_state.case_data,
        "ahp_answers": st.session_state.ahp_answers,
        "portfolio_basket": st.session_state.get("portfolio_basket"),
        "veto_answers": st.session_state.veto_answers,
        "veto_notes": st.session_state.veto_notes,
        "mcda_answers": st.session_state.mcda_answers,
        "mcda_notes": st.session_state.mcda_notes,
        "counterargument": st.session_state.counterargument,
        "current_step": st.session_state.current_step,
        "mcda_index": st.session_state.mcda_index,
    }


def _require_dict(payload: Mapping[str, Any], key: str) -> dict[str, Any]:
    """Return a required nested draft object or raise a schema error."""
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"'{key}' must be an object/dict.")
    return value


def _require_numeric(value: Any, path: str) -> float:
    """Return a numeric draft value or raise a schema error with its path."""
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"'{path}' must be numeric.") from exc


def validate_portfolio_basket(payload: Mapping[str, Any]) -> None:
    """Validate optional portfolio basket value in an imported draft."""
    if "portfolio_basket" in payload and payload["portfolio_basket"] not in ({None} | BASKET_KEYS):
        raise ValueError("'portfolio_basket' must be 'core', 'growth', 'opportunity', or null.")


def validate_required_draft_keys(payload: Mapping[str, Any]) -> None:
    """Validate required top-level draft keys."""
    missing = REQUIRED_DRAFT_KEYS - set(payload.keys())
    if missing:
        raise ValueError(f"Draft is missing required keys: {', '.join(sorted(missing))}.")


def validate_case_data(case_data: Mapping[str, Any]) -> None:
    """Validate imported case data shape."""
    if "options" in case_data and not isinstance(case_data["options"], list):
        raise ValueError("'case_data.options' must be a list.")


def validate_ahp_answers(ahp_answers: Mapping[str, Any]) -> None:
    """Validate imported AHP pairwise comparison answers."""
    if set(ahp_answers.keys()) != EXPECTED_AHP_KEYS:
        raise ValueError("'ahp_answers' must contain exactly the expected AHP pair keys D01–D10.")
    for pid, value in ahp_answers.items():
        numeric = _require_numeric(value, f"ahp_answers.{pid}")
        if numeric <= 0:
            raise ValueError(f"'ahp_answers.{pid}' must be greater than zero.")


def validate_veto_answers(veto_answers: Mapping[str, Any]) -> None:
    """Validate imported veto checklist answers."""
    if not EXPECTED_VETO_KEYS.issubset(veto_answers.keys()):
        raise ValueError("'veto_answers' is missing one or more expected veto keys.")
    for key in EXPECTED_VETO_KEYS:
        if not isinstance(veto_answers[key], bool):
            raise ValueError(f"'veto_answers.{key}' must be true/false.")


def validate_mcda_answers(mcda_answers: dict[str, Any]) -> None:
    """Validate imported MCDA answers while preserving legacy IRR compatibility."""
    if isinstance(mcda_answers.get("irr"), dict):
        mcda_answers["irr"] = None
    expected_mcda = {c["key"] for c in CRITERIA}
    if set(mcda_answers.keys()) != expected_mcda:
        raise ValueError("'mcda_answers' must contain exactly the expected MCDA criterion keys.")

    for c in CRITERIA:
        key = c["key"]
        value = mcda_answers[key]
        if c["type"] == "scale":
            if value is not None:
                _require_numeric(value, f"mcda_answers.{key}")
        else:
            if not isinstance(value, dict):
                raise ValueError(f"'mcda_answers.{key}' must be an object/dict.")
            required_fields = {"value", "min", "max"} if c["type"] == "benefit" else {"value", "ideal", "worst"}
            if set(value.keys()) != required_fields:
                raise ValueError(f"'mcda_answers.{key}' must contain fields: {', '.join(sorted(required_fields))}.")
            for field in required_fields:
                if value[field] not in (None, ""):
                    _require_numeric(value[field], f"mcda_answers.{key}.{field}")


def validate_navigation_state(payload: Mapping[str, Any]) -> None:
    """Validate optional wizard navigation fields in an imported draft."""
    if "current_step" in payload and payload["current_step"] not in PAGE_KEYS:
        raise ValueError("'current_step' has an unknown value.")
    if "mcda_index" in payload:
        idx = int(_require_numeric(payload["mcda_index"], "mcda_index"))
        if idx < 0 or idx >= len(DOMAINS):
            raise ValueError("'mcda_index' is out of range.")


def validate_draft_schema(payload: Any) -> None:
    """Validate an imported decision draft before applying it to session state."""
    if not isinstance(payload, dict):
        raise ValueError("Draft root must be a JSON object.")

    validate_portfolio_basket(payload)
    validate_required_draft_keys(payload)
    validate_case_data(_require_dict(payload, "case_data"))
    validate_ahp_answers(_require_dict(payload, "ahp_answers"))
    validate_veto_answers(_require_dict(payload, "veto_answers"))

    if not isinstance(payload.get("veto_notes"), dict):
        raise ValueError("'veto_notes' must be an object/dict.")

    validate_mcda_answers(_require_dict(payload, "mcda_answers"))

    if not isinstance(payload.get("mcda_notes"), dict):
        raise ValueError("'mcda_notes' must be an object/dict.")

    validate_navigation_state(payload)

def import_draft(payload: dict[str, Any]) -> None:
    """Import a validated decision draft into Streamlit session state."""
    validate_draft_schema(payload)
    for key in ALLOWED_IMPORT_KEYS:
        if key in payload:
            st.session_state[key] = payload[key]
    if st.session_state.get("current_step") == "case":
        st.session_state.current_step = "ahp"
    calculate_ahp()
    calculate_scores()


def page_welcome() -> None:
    render_header()
    render_premium_page_header(
        "Decision Framework",
        "Система для структурованого ухвалення стратегічних рішень",
        progress=8,
    )

    st.markdown(
        """
        <div class='df-intro-layout'>
          <div class='df-intro-card df-intro-note'>
            <h3>Для кого цей інструмент</h3>
            <p>Для людей, які одночасно керують кількома джерелами доходу або зонами відповідальності: бізнесом, роботою, інвестиціями, нерухомістю, партнерськими проєктами чи новими можливостями.</p>
            <p>Коли таких напрямів стає кілька, вони починають конкурувати не лише за гроші, а й за час, увагу, фокус і управлінську енергію.</p>
          </div>
          <div class='df-intro-card'>
            <h3>Для чого цей інструмент</h3>
            <p>Decision Framework допомагає оцінити, чи варто зберігати, посилювати, змінювати або закривати напрям / актив / можливість.</p>
            <p>Модель порівнює фінансові та нефінансові критерії: дохідність, cash flow, керованість, навантаження, стратегічну значущість і особисту сумісність.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='df-outcome-card'>
          <div class='df-outcome-title'>На виході ви отримаєте</div>
          <div class='df-outcome-grid'>
            <div class='df-outcome-chip'>100-бальна оцінка</div>
            <div class='df-outcome-chip'>Рекомендації</div>
            <div class='df-outcome-chip'>Ключові ризики</div>
            <div class='df-outcome-chip'>Decision memo</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='df-stepper-card'>
          <div class='df-stepper-title'>Маршрут оцінки</div>
          <div class='df-stepper'>
            <div class='df-stepper-step'><span class='df-stepper-num'>1</span><span class='df-stepper-label'>Ваги</span></div>
            <div class='df-stepper-step'><span class='df-stepper-num'>2</span><span class='df-stepper-label'>Роль у портфелі</span></div>
            <div class='df-stepper-step'><span class='df-stepper-num'>3</span><span class='df-stepper-label'>Стоп-фактори</span></div>
            <div class='df-stepper-step'><span class='df-stepper-num'>4</span><span class='df-stepper-label'>MCDA</span></div>
            <div class='df-stepper-step'><span class='df-stepper-num'>5</span><span class='df-stepper-label'>Панель рішення</span></div>
            <div class='df-stepper-step'><span class='df-stepper-num'>6</span><span class='df-stepper-label'>Memo</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="welcome_cta"):
        if st.button("Почати дослідження", type="primary", use_container_width=True):
            reset_decision_state("ahp")

def render_ahp_guide() -> None:
    """Render the static AHP instruction panel."""
    st.markdown(
        """
        <div class='df-ahp-guide'>
            <div class='df-ahp-guide-title'>Як відповідати:</div>
            <ul>
                <li>Не оцінюйте «взагалі по життю». Оцінюйте свій фактичний профіль на найближчі 12–24 місяці.</li>
                <li>Спирайтеся не на самоопис, а на факти: минулі рішення, поведінку в кризі, реальні обмеження часу, реакцію на просадки, делегування, потребу в ліквідності.</li>
                <li>Якщо сумніваєтеся між двома оцінками, оберіть консервативнішу.</li>
                <li>Якщо Consistency Ratio (CR) &gt; 0.10, поверніться до тих пар, де відповідь була найрізкішою або суперечила іншим компромісам.</li>
                <li>Поставте собі питання: «Якби мене змусили пожертвувати одним із двох, що я захищав би першим саме зараз?»</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ahp_comparison_card(pid: str) -> None:
    """Render one AHP pair comparison card and persist the selected answer."""
    left, right = PAIR_LOOKUP[pid]
    left_label = ahp_domain_label(left)
    right_label = ahp_domain_label(right)
    idx = ahp_pair_radio_index(pid)
    option_indices = list(range(len(PAIRWISE_OPTIONS)))

    with st.container(border=True):
        st.markdown(
            f"""
            <div class='df-ahp-title'>
                <span>{escape(left_label)}</span>
                <span class='vs'>vs</span>
                <span>{escape(right_label)}</span>
            </div>
            <div class='df-ahp-scale-caption'>
                <span>{escape(left_label)} важливіше</span>
                <span>{escape(right_label)} важливіше</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        option_cols = st.columns(len(PAIRWISE_OPTIONS), gap="small")
        for option_idx, (option_key, _) in enumerate(PAIRWISE_OPTIONS):
            choice_key = f"ahp_choice_{pid}_{option_key}"
            left_color, right_color = ahp_choice_strip_colors(left, right, option_key)
            with option_cols[option_idx]:
                with st.container(key=choice_key):
                    render_ahp_choice_style(choice_key, left_color, right_color, idx == option_idx)
                    clicked = st.button(
                        AHP_OPTION_LABELS[option_key],
                        key=f"ahp_btn_{pid}_{option_key}",
                        type="secondary",
                        use_container_width=True,
                    )
                    if clicked:
                        set_ahp_pair_answer(pid, option_idx)
                        st.rerun()

        st.markdown(
            f"""
            <div class='df-domain-desc-grid'>
                {domain_description_card(left)}
                {domain_description_card(right)}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_ahp_input_panel() -> None:
    """Render all currently revealed AHP comparison cards."""
    render_ahp_guide()
    revealed_pairs = ahp_revealed_pairs()
    for pid in revealed_pairs:
        render_ahp_comparison_card(pid)

    answered_count = len(ahp_answered_pairs())
    if answered_count < len(PAIRWISE):
        st.caption(f"Показано {len(revealed_pairs)} з {len(PAIRWISE)} порівнянь. Наступне з’явиться після відповіді на поточне.")


def render_ahp_weight_meter(domain: DomainConfig, weight: float) -> None:
    """Render one AHP domain weight row with a pedestal input."""
    p_col, w_col = st.columns([0.14, 0.86], gap="small")
    with p_col:
        raw_pedestal = st.text_input(
            f"Попередня оцінка {domain['label']}",
            placeholder="",
            max_chars=1,
            label_visibility="collapsed",
            key=f"pedestal_{domain['key']}",
        )
        if raw_pedestal and raw_pedestal not in {"1", "2", "3", "4", "5"}:
            st.session_state[f"pedestal_{domain['key']}"] = ""
            st.rerun()
    with w_col:
        st.markdown(
            f"""
            <div class='df-weight-meter'>
                <div class='df-weight-meter-label'><span>{escape(domain['label'])}</span><b>{weight * 100:.1f}%</b></div>
                <div class='df-weight-track'><div class='df-weight-fill' style='width:{max(0, min(100, weight * 100)):.1f}%;'></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_ahp_consistency_panel(cr: float, warnings: Sequence[Mapping[str, Any]]) -> None:
    """Render AHP consistency ratio and conflict hints."""
    cr_kind = "good" if cr <= AHP_CR_WARNING_THRESHOLD else "warn"
    cr_text = "Оцінки узгоджені." if cr <= AHP_CR_WARNING_THRESHOLD else "Є логічна неузгодженість. Переглянь підсвічені порівняння."
    st.markdown(
        f"""
        <div class='df-cr-card {cr_kind}'>
            <div class='cr'>CR {cr:.3f}</div>
            <div class='caption'>{cr_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if cr > AHP_CR_WARNING_THRESHOLD:
        for item in list(warnings)[:3]:
            a, b, c = [DOMAIN_BY_KEY[x]["label"] for x in item["triad"]]
            body = (
                f"<b>Тріада:</b> {a} → {b} → {c}<br>"
                f"<b>Фактичне A/C:</b> {item['actual']:.2f}; <b>логічно очікуване:</b> {item['expected']:.2f}"
            )
            card("Можлива суперечність", body, "amber")
        for hint in ahp_pattern_hints():
            st.info(hint)


def render_ahp_result_panel(weights: Mapping[str, float], cr: float, warnings: Sequence[Mapping[str, Any]]) -> None:
    """Render the fixed AHP result panel."""
    with st.container(key="ahp_result_sticky"):
        st.markdown("<div class='df-ahp-layout-title'>Результат калібрування</div>", unsafe_allow_html=True)
        for domain in DOMAINS:
            render_ahp_weight_meter(domain, float(weights.get(domain["key"], 0.0)))
        render_ahp_consistency_panel(cr, warnings)


def render_ahp_navigation(cr: float) -> None:
    """Render AHP page navigation controls."""
    answered_count = len(ahp_answered_pairs())
    all_answered = answered_count >= len(PAIRWISE)
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("Назад до вступу", use_container_width=True):
            go(PAGE_WELCOME)
    with c2:
        next_label = "Продовжити попри CR" if cr > AHP_CR_WARNING_THRESHOLD else "Продовжити до ролі"
        if st.button(next_label, type="primary", use_container_width=True, disabled=not all_answered):
            go(PAGE_BASKET)
    if not all_answered:
        st.caption(f"Щоб перейти далі, завершіть усі попарні порівняння: {answered_count}/{len(PAIRWISE)}.")


def page_ahp() -> None:
    """Render the AHP calibration step."""
    render_header()
    render_premium_page_header(
        "Визначення ваги кожного домену",
        "Тут ти не оцінюєш конкретний актив чи рішення. Ти визначаєш, які критерії загалом важливіші для якісного рішення.",
        progress=22,
    )

    ensure_ahp_flow_state()
    sync_ahp_answers_from_widgets()
    _, weights, cr, warnings = calculate_ahp()

    input_col, result_col = st.columns([1.75, 0.75], gap="medium")
    with input_col:
        render_ahp_input_panel()

    sync_ahp_answers_from_widgets()
    _, weights, cr, warnings = calculate_ahp()
    with result_col:
        render_ahp_result_panel(weights, cr, warnings)

    render_ahp_navigation(cr)


def page_basket() -> None:
    render_header()
    render_premium_page_header("Роль у портфелі", "Перш ніж оцінювати актив — визначте, яку роль він має виконувати у вашому портфелі. Загальна шкала score однакова, але кожен кошик має власний admission threshold.", progress=36)

    basket_keys = ["core", "growth", "opportunity"]
    current = st.session_state.get("portfolio_basket")
    index = radio_index_from_value(basket_keys, current)

    with st.form("basket_form"):
        selected = st.radio(
            "Portfolio role",
            basket_keys,
            index=index,
            format_func=basket_option_label,
            label_visibility="collapsed",
            horizontal=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            back = st.form_submit_button("Назад до AHP", use_container_width=True)
        with c2:
            cont = st.form_submit_button("Продовжити до стоп-факторів", type="primary", use_container_width=True)

    if back:
        go("ahp")
    if cont and selected is not None:
        st.session_state.portfolio_basket = selected
        go("veto")

    if current:
        cfg = BASKET_CONFIG[current]
        st.success(f"Поточний кошик: **{cfg['label']}**.")


def render_review_protocol_table() -> None:
    rows = []
    for r in REVIEW_PROTOCOLS:
        rows.append(
            f"<tr>"
            f"<td>{escape(r['size'])}</td>"
            f"<td>{escape(r['mode'])}</td>"
            f"<td>{escape(r['action'])}</td>"
            f"<td>{escape(r['validation'])}</td>"
            f"</tr>"
        )
    st.markdown(
        "<table class='df-review-table'>"
        "<thead><tr><th>Розмір рішення</th><th>Режим</th><th>Обов’язкова дія</th><th>Перевірка перед дією</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        f"<div class='df-prem-hint'>{escape(REVIEW_PROTOCOL_NOTE)}</div>",
        unsafe_allow_html=True,
    )


def render_veto_status_bar(vetoes: Sequence[Mapping[str, Any]]) -> None:
    if vetoes:
        names = ", ".join(v["name"] for v in vetoes[:3])
        extra = f" +{len(vetoes) - 3}" if len(vetoes) > 3 else ""
        st.markdown(
            f"""
            <div class='df-risk-status-bar warn'>
              <div><span class='df-risk-status-main'>Активовано стоп-факторів: {len(vetoes)}</span></div>
              <div class='df-risk-status-meta'>{escape(names + extra)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class='df-risk-status-bar good'>
              <div><span class='df-risk-status-main'>Стоп-фактори: норма</span></div>
              <div class='df-risk-status-meta'>Активних стоп-факторів немає</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_veto_group(group: Mapping[str, Any]) -> None:
    active_count = sum(1 for key, _ in group["items"] if st.session_state.veto_answers.get(key, False))
    title = f"{group['title']} · {active_count}/{len(group['items'])}"
    expanded = active_count > 0

    with st.expander(title, expanded=expanded):
        st.markdown(f"<div class='df-risk-group-note'>{escape(group['description'])}</div>", unsafe_allow_html=True)
        for key, severity in group["items"]:
            item = VETO_BY_KEY[key]
            cols = st.columns([0.42, 1.58, 0.42], gap="small")
            with cols[0]:
                checked = st.checkbox(
                    item["name"],
                    value=st.session_state.veto_answers.get(item["key"], False),
                    key=f"veto_{item['key']}",
                )
                st.session_state.veto_answers[item["key"]] = checked
            with cols[1]:
                signal = f"<div class='df-risk-signal'>Сигнал: {escape(item['signal'])}</div>" if checked else ""
                st.markdown(
                    f"<div class='df-risk-row-meta'><div class='df-risk-desc'>{escape(item['description'])}</div>{signal}</div>",
                    unsafe_allow_html=True,
                )
            with cols[2]:
                cls = VETO_SEVERITY_CLASS.get(severity, "review")
                label = VETO_SEVERITY_LABELS.get(severity, severity)
                st.markdown(f"<span class='df-risk-badge {cls}'>{escape(label)}</span>", unsafe_allow_html=True)


def page_veto() -> None:
    render_header()
    render_premium_page_header(
        "Стоп-фактори",
        "Risk-control checkpoint перед MCDA: перевіряє фінансові, операційні та поведінкові ризики, які можуть вимагати перегляду рішення.",
        progress=50,
    )

    vetoes = active_vetoes()
    render_veto_status_bar(vetoes)

    for group in VETO_RISK_GROUPS:
        render_veto_group(group)

    st.markdown("### Протокол перегляду")
    render_review_protocol_table()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Назад до ролі", use_container_width=True):
            go("basket")
    with c2:
        if st.button("Почати MCDA", type="primary", use_container_width=True):
            go("mcda", 0)



def mcda_current_value(c: Mapping[str, Any]) -> Any:
    """Return the freshest UI value for completion checks."""
    ctype = c.get("type")
    key = c["key"]

    if ctype == "scale":
        radio_key = f"mcda_radio_{key}"
        return st.session_state.get(radio_key, st.session_state.mcda_answers.get(key))

    if ctype == "benefit":
        answer = dict(st.session_state.mcda_answers.get(key, c.get("default", {})))
        for field in ("value", "min", "max"):
            widget_key = f"num_{key}_{field}"
            if widget_key in st.session_state:
                answer[field] = st.session_state[widget_key]
        return answer

    if ctype == "cost":
        answer = dict(st.session_state.mcda_answers.get(key, c.get("default", {})))
        for field in ("value", "ideal", "worst"):
            widget_key = f"num_{key}_{field}"
            if widget_key in st.session_state:
                answer[field] = st.session_state[widget_key]
        return answer

    return st.session_state.mcda_answers.get(key, c.get("default"))


def benefit_initial_value(c: Mapping[str, Any], field: str) -> str:
    answer = dict(st.session_state.mcda_answers.get(c["key"], c.get("default", {})))
    raw = answer.get(field, "")
    if raw is None or raw == "":
        return ""
    parsed = parse_optional_int(raw)
    return "" if parsed is None else str(parsed)


def benefit_raw_values(c: Mapping[str, Any]) -> tuple[str, str, str]:
    key = c["key"]
    values = {}
    for field in ("value", "min", "max"):
        widget_key = f"num_{key}_{field}"
        if widget_key in st.session_state:
            values[field] = st.session_state[widget_key]
        else:
            values[field] = benefit_initial_value(c, field)
    return values


def benefit_dirty(c: Mapping[str, Any]) -> bool:
    raw = benefit_raw_values(c)
    default_min = str(c.get("default", {}).get("min", ""))
    return (
        str(raw.get("value", "")).strip() != "" or
        str(raw.get("max", "")).strip() != "" or
        str(raw.get("min", "")).strip() not in {"", default_min}
    )


def benefit_errors(c: Mapping[str, Any], show_errors: bool = False) -> list[str]:
    raw = benefit_raw_values(c)
    errors = {"value": "", "min": "", "max": ""}

    parsed = {}
    for field in ("value", "min", "max"):
        value_raw = str(raw.get(field, "")).strip()
        if value_raw == "":
            parsed[field] = None
            if show_errors:
                errors[field] = "Вкажіть значення."
        elif value_raw.startswith("-"):
            parsed[field] = None
            if show_errors:
                errors[field] = "Значення не може бути від’ємним."
        else:
            parsed[field] = parse_optional_int(value_raw)
            if parsed[field] is None and show_errors:
                errors[field] = "Вкажіть ціле число."

    if show_errors and parsed.get("min") is not None and parsed.get("max") is not None:
        if parsed["max"] <= parsed["min"]:
            errors["max"] = "Має бути вище мінімуму."

    return errors, parsed


def benefit_state(c: Mapping[str, Any]) -> tuple[bool, float | None, list[str]]:
    raw = benefit_raw_values(c)
    attempted = bool(st.session_state.get(f"mcda_attempted_{c['key']}", False))
    show_errors = attempted or benefit_dirty(c)
    errors, parsed = benefit_errors(c, show_errors=show_errors)

    filled_fields = [str(raw.get(field, "")).strip() != "" for field in ("value", "min", "max")]
    has_any = any(filled_fields)
    has_error = any(errors.values())
    complete = (
        parsed.get("value") is not None and
        parsed.get("min") is not None and
        parsed.get("max") is not None and
        parsed["max"] > parsed["min"]
    )

    if complete:
        return "complete"
    if has_error and show_errors:
        return "error"
    if has_any:
        return "progress"
    return "empty"


def cost_initial_value(c: Mapping[str, Any], field: str) -> str:
    answer = dict(st.session_state.mcda_answers.get(c["key"], c.get("default", {})))
    raw = answer.get(field, "")
    if raw is None or raw == "":
        return ""
    parsed = parse_optional_int(raw)
    return "" if parsed is None else str(parsed)


def cost_raw_values(c: Mapping[str, Any]) -> tuple[str, str, str]:
    key = c["key"]
    values = {}
    for field in ("value", "ideal", "worst"):
        widget_key = f"num_{key}_{field}"
        if widget_key in st.session_state:
            values[field] = st.session_state[widget_key]
        else:
            values[field] = cost_initial_value(c, field)
    return values


def cost_dirty(c: Mapping[str, Any]) -> bool:
    raw = cost_raw_values(c)
    return any(str(raw.get(field, "")).strip() != "" for field in ("value", "ideal", "worst"))


def cost_errors(c: Mapping[str, Any], show_errors: bool = False) -> list[str]:
    raw = cost_raw_values(c)
    errors = {"value": "", "ideal": "", "worst": ""}
    parsed = {}
    for field in ("value", "ideal", "worst"):
        value_raw = str(raw.get(field, "")).strip()
        if value_raw == "":
            parsed[field] = None
            if show_errors:
                errors[field] = "Вкажіть значення."
        elif value_raw.startswith("-"):
            parsed[field] = None
            if show_errors:
                errors[field] = "Значення не може бути від’ємним."
        else:
            parsed[field] = parse_optional_int(value_raw)
            if parsed[field] is None and show_errors:
                errors[field] = "Вкажіть ціле число."

    if show_errors and parsed.get("ideal") is not None and parsed.get("worst") is not None:
        if parsed["worst"] <= parsed["ideal"]:
            errors["worst"] = "Має бути вище комфортного рівня."
    return errors, parsed


def cost_state(c: Mapping[str, Any]) -> tuple[bool, float | None, list[str]]:
    raw = cost_raw_values(c)
    attempted = bool(st.session_state.get(f"mcda_attempted_{c['key']}", False))
    show_errors = attempted or cost_dirty(c)
    errors, parsed = cost_errors(c, show_errors=show_errors)
    filled_fields = [str(raw.get(field, "")).strip() != "" for field in ("value", "ideal", "worst")]
    has_any = any(filled_fields)
    has_error = any(errors.values())
    complete = (
        parsed.get("value") is not None and
        parsed.get("ideal") is not None and
        parsed.get("worst") is not None and
        parsed["worst"] > parsed["ideal"]
    )
    if complete:
        return "complete"
    if has_error and show_errors:
        return "error"
    if has_any:
        return "progress"
    return "empty"


def mcda_criterion_complete(c: Mapping[str, Any]) -> bool:
    answer = mcda_current_value(c)
    if c["type"] == "scale":
        return answer is not None
    if c["type"] == "benefit":
        return benefit_state(c) == "complete"
    if c["type"] == "cost":
        return cost_state(c) == "complete"
    return False


def mcda_domain_completion(domain_criteria: Sequence[Mapping[str, Any]]) -> int:
    completed = sum(1 for c in domain_criteria if mcda_criterion_complete(c))
    return completed, len(domain_criteria)


def mcda_status_badge(c: Mapping[str, Any]) -> str:
    if c["type"] == "benefit":
        state = benefit_state(c)
    elif c["type"] == "cost":
        state = cost_state(c)
    else:
        state = "complete" if mcda_criterion_complete(c) else "empty"
    if state == "complete":
        return "<span class='df-prem-status done'>Оцінено</span>"
    if state == "error":
        return "<span class='df-prem-status error'>Є помилка</span>"
    if state == "progress":
        return "<span class='df-prem-status progress'>В процесі</span>"
    return "<span class='df-prem-status missing'>Не заповнено</span>"


def render_mcda_criterion_header(c: Mapping[str, Any]) -> None:
    badge = mcda_status_badge(c)
    return f"""
    <div class='df-prem-criterion-head'>
      <div>
        <div class='df-prem-criterion-title'>{escape(c['name'])}</div>
        <div class='df-prem-criterion-desc'>{escape(c.get('what', ''))}</div>
      </div>
      {badge}
    </div>
    """

def render_mcda_page_header(domain_idx: int, domain: DomainConfig) -> None:
    """Render the MCDA domain header and progress."""
    progress_pct = (domain_idx + 1) / len(DOMAINS) * 100
    st.markdown(
        f"""
        <div class='df-prem-page-head'>
          <div>
            <div class='df-prem-title'>MCDA · {escape(domain['label'])}</div>
            <div class='df-prem-meta'>Крок {domain_idx + 1} з {len(DOMAINS)}</div>
          </div>
        </div>
        <div class='df-prem-progress'><div class='df-prem-progress-fill' style='width:{progress_pct:.1f}%;'></div></div>
        <div class='df-prem-domain-card'>
          <div class='df-prem-domain-title'>{escape(domain['label'])}</div>
          <div class='df-prem-domain-subtitle'>{escape(mcda_domain_summary(domain['key']))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_field_error(message: str) -> None:
    """Render one inline field validation error."""
    if message:
        st.markdown(f"<div class='df-field-error'>{message}</div>", unsafe_allow_html=True)


def render_mcda_scale_input(c: CriterionConfig) -> None:
    """Render and persist a scale-based MCDA criterion."""
    selected = st.radio(
        f"MCDA anchor {c['key']}",
        options=SCALE_ANCHORS,
        index=scale_anchor_index(c),
        format_func=lambda value, crit=c: scale_anchor_label(crit, value),
        horizontal=True,
        label_visibility="collapsed",
        key=f"mcda_radio_{c['key']}",
    )
    if selected is not None:
        st.session_state.mcda_answers[c["key"]] = float(selected)


def render_mcda_benefit_input(c: CriterionConfig) -> None:
    """Render and persist a benefit numeric MCDA criterion."""
    answer = dict(st.session_state.mcda_answers.get(c["key"], c["default"]))
    field_specs = [
        ("min", c["min_label"], "введи %"),
        ("value", c["input_label"], "введи %"),
        ("max", c["max_label"], "введи %"),
    ]
    show_errors = bool(st.session_state.get(f"mcda_attempted_{c['key']}", False)) or benefit_dirty(c)
    errors, _ = benefit_errors(c, show_errors=show_errors)

    st.markdown("<div class='df-finance-value-group'>", unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    for idx, (field, label, placeholder) in enumerate(field_specs):
        with cols[idx]:
            raw = st.text_input(
                label,
                value=benefit_initial_value(c, field),
                placeholder=placeholder,
                key=f"num_{c['key']}_{field}",
            )
            answer[field] = parse_optional_int(raw)
            render_field_error(errors.get(field, ""))
    st.markdown("</div>", unsafe_allow_html=True)
    st.session_state.mcda_answers[c["key"]] = answer


def render_mcda_cost_input(c: CriterionConfig) -> None:
    """Render and persist a cost numeric MCDA criterion."""
    answer = dict(st.session_state.mcda_answers.get(c["key"], c["default"]))
    field_specs = [
        ("value", c["input_label"], "напр. 8"),
        ("ideal", c["ideal_label"], "напр. 5"),
        ("worst", c["worst_label"], "напр. 20"),
    ]
    show_errors = bool(st.session_state.get(f"mcda_attempted_{c['key']}", False)) or cost_dirty(c)
    errors, _ = cost_errors(c, show_errors=show_errors)

    st.markdown("<div class='df-finance-value-group'>", unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    for idx, (field, label, placeholder) in enumerate(field_specs):
        with cols[idx]:
            raw = st.text_input(
                label,
                value=cost_initial_value(c, field),
                placeholder=placeholder,
                key=f"num_{c['key']}_{field}",
            )
            answer[field] = parse_optional_int(raw)
            render_field_error(errors.get(field, ""))
    st.markdown("</div>", unsafe_allow_html=True)
    st.session_state.mcda_answers[c["key"]] = answer

    if cost_state(c) == "complete" and answer.get("value") is not None and answer.get("worst") is not None and answer["value"] > answer["worst"]:
        st.warning("Введене навантаження гірше за найгірше допустиме значення. Бал буде обрізано до 0; це сигнал для доопрацювання / перегляду стоп-факторів.")


def render_mcda_criterion(c: CriterionConfig) -> None:
    """Render one MCDA criterion card according to its input type."""
    with st.container(border=True):
        header_slot = st.empty()
        evidence_html = ""
        if c.get("evidence"):
            evidence_html = f"<div class='df-prem-hint'><strong>Що врахувати:</strong> {escape(str(c.get('evidence', '')))}</div>"

        if c["type"] == "scale":
            render_mcda_scale_input(c)
        elif c["type"] == "benefit":
            render_mcda_benefit_input(c)
        elif c["type"] == "cost":
            render_mcda_cost_input(c)

        # Fill the header after widgets are rendered so status badges use the freshest state.
        header_slot.markdown(render_mcda_criterion_header(c), unsafe_allow_html=True)

        if evidence_html:
            st.markdown(evidence_html, unsafe_allow_html=True)


def mark_mcda_attempted(domain_criteria: Sequence[CriterionConfig]) -> None:
    """Mark numeric MCDA criteria as attempted so validation errors become visible."""
    for crit in domain_criteria:
        if crit["type"] in {"benefit", "cost"}:
            st.session_state[f"mcda_attempted_{crit['key']}"] = True


def render_mcda_navigation(domain_idx: int, domain_criteria: Sequence[CriterionConfig]) -> None:
    """Render MCDA navigation and completion guard."""
    completed, total = mcda_domain_completion(domain_criteria)
    domain_ready = completed == total
    st.markdown("<div class='df-prem-nav-spacer'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Назад", use_container_width=True):
            go(PAGE_VETO if domain_idx == 0 else PAGE_MCDA, None if domain_idx == 0 else domain_idx - 1)
    with c2:
        next_label = "Далі" if domain_idx < len(DOMAINS) - 1 else "До панелі рішення"
        if st.button(next_label, type="primary", use_container_width=True):
            if not domain_ready:
                mark_mcda_attempted(domain_criteria)
                st.rerun()
            elif domain_idx < len(DOMAINS) - 1:
                go(PAGE_MCDA, domain_idx + 1)
            else:
                calculate_scores()
                go(PAGE_DASHBOARD)
    if not domain_ready:
        st.caption("Щоб перейти далі, заповніть усі критерії на цій сторінці.")


def page_mcda() -> None:
    """Render the active MCDA domain step."""
    render_header()
    domain_idx = mcda_domain_index()
    st.session_state.mcda_index = domain_idx
    domain = DOMAINS[domain_idx]
    domain_criteria = criteria_for_domain(domain["key"])

    render_mcda_page_header(domain_idx, domain)
    for criterion in domain_criteria:
        render_mcda_criterion(criterion)
    render_mcda_navigation(domain_idx, domain_criteria)


def status_visual_kind(status: str) -> str:
    status_text = str(status or "")
    if "EXIT" in status_text or "GATE REVIEW" in status_text:
        return "bad"
    if "REFACTOR" in status_text or "REVIEW" in status_text:
        return "warn"
    return "good"


def score_band_label(score: float) -> str:
    if score >= 80:
        return "сильне рішення"
    if score >= 65:
        return "прийнятно, є ризики"
    if score >= 50:
        return "потребує доопрацювання"
    return "нижче мінімуму"


def domain_interpretation(score: float) -> str:
    if score >= 80:
        return "сильний"
    if score >= 65:
        return "прийнятний"
    if score >= 50:
        return "змішаний"
    return "слабкий"


def safe_score(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0


def display_answer_value(raw: Any) -> str:
    if raw is None or raw == "":
        return "—"
    try:
        value = float(raw)
        if value.is_integer():
            return str(int(value))
        return f"{value:.1f}"
    except (TypeError, ValueError, OverflowError):
        return str(raw)


def scoring_type_label(kind: str) -> str:
    return {"scale": "шкала", "benefit": "вигода", "cost": "витрати"}.get(str(kind), str(kind))


def subcriterion_input_display(c: Mapping[str, Any]) -> str:
    answer = st.session_state.mcda_answers.get(c["key"])
    if c["type"] == "scale":
        return f"{display_answer_value(answer)} / 10"
    if c["type"] == "benefit" and isinstance(answer, dict):
        return (
            f"мін. {display_answer_value(answer.get('min'))} · "
            f"база {display_answer_value(answer.get('value'))} · "
            f"макс. {display_answer_value(answer.get('max'))}"
        )
    if c["type"] == "cost" and isinstance(answer, dict):
        return (
            f"факт {display_answer_value(answer.get('value'))} год · "
            f"план {display_answer_value(answer.get('ideal'))} год · "
            f"межа {display_answer_value(answer.get('worst'))} год"
        )
    return "—"


def domain_subcriteria_rank(domain_key: str, criterion_scores: Mapping[str, float]) -> list[tuple[Mapping[str, Any], float]]:
    items = [c for c in CRITERIA if c["domain"] == domain_key]
    if not items:
        return None, None
    strongest = max(items, key=lambda c: safe_score(criterion_scores.get(c["key"], 0)))
    weakest = min(items, key=lambda c: safe_score(criterion_scores.get(c["key"], 0)))
    return strongest, weakest


def fragility_index(c: Mapping[str, Any], criterion_scores: Mapping[str, float]) -> float:
    return st.session_state.ahp_weights.get(c["domain"], 0.0) * (1 - safe_score(criterion_scores.get(c["key"], 0)))


def fragility_tags(c: Mapping[str, Any], score: float, fragility: float) -> list[str]:
    tags = []
    if score < 40:
        tags.append(("Низький бал", "bad"))
    elif score < 65:
        tags.append(("Слабке місце", "warn"))
    if st.session_state.ahp_weights.get(c["domain"], 0.0) >= 0.20:
        tags.append(("Висока вага", "warn"))
    if c["domain"] == "economic_quality" and score < 60:
        tags.append(("Ризик порогу", "bad"))
    if fragility >= 10:
        tags.append(("Потрібен перегляд", "warn"))
    return tags or [("Норма", "good")]


def fragility_action(c: Mapping[str, Any], score: float) -> str:
    if score < 40:
        return "Переробити"
    if c["domain"] in {"economic_quality", "asset_controllability"} and score < 60:
        return "Явний перегляд"
    if score < 65:
        return "Покращити"
    return "Моніторити"


def render_dashboard_kpi(label: str, value: str, note: str, kind: str = "neutral") -> None:
    cls = "df-dashboard-kpi"
    if kind in {"good", "warn", "bad"}:
        cls += f" {kind}"
    st.markdown(
        f"<div class='{cls}'><div><div class='kpi-label'>{escape(str(label))}</div>"
        f"<div class='kpi-value'>{escape(str(value))}</div></div>"
        f"<div class='kpi-note'>{escape(str(note))}</div></div>",
        unsafe_allow_html=True,
    )


def render_recommendation_panel(status: str, final: float, vetoes: Sequence[Mapping[str, Any]], gates: Sequence[str]) -> None:
    kind = status_visual_kind(status)
    base = base_status(final)
    if gates:
        body = (
            f"Базовий результат: <b>{escape(base)}</b>. Фінальний статус: <b>{escape(status)}</b>. "
            f"Причина: порушено поріг «{escape('; '.join(gates))}». "
            "Це не veto, але перед дією потрібні доопрацювання або явний перегляд власником."
        )
    else:
        body = (
            f"Базовий результат: <b>{escape(base)}</b>. Фінальний статус: <b>{escape(status)}</b>. "
            f"{escape(recommendation_text(final, status, vetoes, gates))}"
        )
    st.markdown(
        f"<div class='df-recommendation-panel {kind}'>"
        f"<div class='df-recommendation-title'>Рекомендація · {escape(status)}</div>"
        f"<div class='df-recommendation-body'>{body}</div></div>",
        unsafe_allow_html=True,
    )


def score_explain_rows(domain_scores: Mapping[str, float], criterion_scores: Mapping[str, float], gates: Sequence[str]) -> list[str]:
    weights = st.session_state.ahp_weights or {}
    rows = []
    for d in DOMAINS:
        key = d["key"]
        score = safe_score(domain_scores.get(key, 0))
        вага = safe_score(weights.get(key, 0))
        contribution = score * вага
        weighted_drag = вага * (100 - score)
        _, lowest = domain_subcriteria_rank(key, criterion_scores)
        lowest_text = "—"
        if lowest is not None:
            lowest_score = safe_score(criterion_scores.get(lowest["key"], 0)) * 100
            lowest_text = f"Найнижчий: {lowest['name']} ({lowest_score:.0f})"
        gate_status = "норма"
        if key == "economic_quality" and any("Фінанси" in g or "Економічна якість" in g or "Economic Quality" in g for g in gates):
            gate_status = "порушено"
        elif key == "asset_controllability" and any("Керованість" in g or "Керованість активу" in g or "Asset Controllability" in g for g in gates):
            gate_status = "порушено"
        rows.append({
            "key": key,
            "domain": d["label"],
            "score": score,
            "weight": вага,
            "contribution": contribution,
            "weighted_drag": weighted_drag,
            "lowest": lowest_text,
            "gate_status": gate_status,
        })
    return rows



def render_score_explain_table(domain_scores: Mapping[str, float], criterion_scores: Mapping[str, float], final: float, gates: Sequence[str]) -> None:
    rows = score_explain_rows(domain_scores, criterion_scores, gates)
    max_contrib = max(rows, key=lambda r: r["contribution"])["key"] if rows else None
    max_drag = max(rows, key=lambda r: r["weighted_drag"])["key"] if rows else None
    html_rows = []
    for r in rows:
        chips = []
        if r["key"] == max_contrib:
            chips.append("<span class='df-risk-chip good'>найбільше підсилює</span>")
        if r["key"] == max_drag:
            chips.append("<span class='df-risk-chip bad'>найбільше тисне вниз</span>")
        gate_kind = "bad" if r["gate_status"] == "порушено" else "good"
        html_rows.append(
            "<tr>"
            f"<td><b>{escape(r['domain'])}</b><br>{''.join(chips)}</td>"
            f"<td><div class='df-scorebar-wrap'><div class='df-mini-bar'><div class='df-mini-bar-fill' style='width:{max(0, min(100, r['score'])):.1f}%;'></div></div><div class='df-scorebar-label'>{r['score']:.1f} / 100</div></div></td>"
            f"<td>{r['weight'] * 100:.1f}%</td>"
            f"<td><b>{r['contribution']:.1f}</b></td>"
            f"<td>{escape(r['lowest'])}</td>"
            f"<td><span class='df-risk-chip {gate_kind}'>{escape(r['gate_status'])}</span></td>"
            "</tr>"
        )
    html_rows.append(
        f"<tr class='sum-row'><td colspan='3'>Підсумковий бал = сума зважених внесків</td><td>{final:.1f}</td><td colspan='2'>Σ бал домену × вага</td></tr>"
    )
    st.markdown(
        "<table class='df-score-table'><thead><tr>"
        "<th>Домен</th><th>Бал</th><th>Вага</th><th>Внесок</th><th>Найнижчий підкритерій</th><th>Статус порогу</th>"
        "</tr></thead><tbody>" + "".join(html_rows) + "</tbody></table>",
        unsafe_allow_html=True,
    )


def render_domain_compact_table(domain_scores: Mapping[str, float], criterion_scores: Mapping[str, float]) -> None:
    rows = []
    for d in DOMAINS:
        key = d["key"]
        score = safe_score(domain_scores.get(key, 0))
        вага = safe_score(st.session_state.ahp_weights.get(key, 0))
        strongest, weakest = domain_subcriteria_rank(key, criterion_scores)
        strongest_text = strongest["name"] if strongest else "—"
        weakest_text = weakest["name"] if weakest else "—"
        rows.append(
            "<tr>"
            f"<td><b>{escape(d['label'])}</b><br><span class='df-muted'>{escape(domain_interpretation(score))}</span></td>"
            f"<td style='min-width:150px'><div class='df-mini-bar'><div class='df-mini-bar-fill' style='width:{max(0, min(100, score)):.1f}%;'></div></div><div class='df-muted'>{score:.1f} / 100</div></td>"
            f"<td>{вага * 100:.1f}%</td>"
            f"<td><span class='df-domain-chip'>найсильніший: {escape(strongest_text)}</span><br><span class='df-domain-chip'>найнижчий: {escape(weakest_text)}</span></td>"
            "</tr>"
        )
    st.markdown(
        "<table class='df-domain-table'><thead><tr>"
        "<th>Домен</th><th>Бал</th><th>Вага</th><th>Драйвери всередині домену</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>",
        unsafe_allow_html=True,
    )


def render_domain_breakdown_accordion(criterion_scores: Mapping[str, float]) -> None:
    for d in DOMAINS:
        domain_criteria = [c for c in CRITERIA if c["domain"] == d["key"]]
        per_sub_weight = 1.0 / len(domain_criteria) if domain_criteria else 0.0
        with st.expander(f"{d['label']} · деталізація підкритеріїв", expanded=False):
            rows = []
            for c in domain_criteria:
                normalized = safe_score(criterion_scores.get(c["key"], 0)) * 100
                contribution = normalized * per_sub_weight
                rows.append(
                    "<tr>"
                    f"<td><b>{escape(c['name'])}</b></td>"
                    f"<td>{escape(subcriterion_input_display(c))}</td>"
                    f"<td>{escape(scoring_type_label(c['type']))}</td>"
                    f"<td>{normalized:.1f}</td>"
                    f"<td>{per_sub_weight * 100:.1f}%</td>"
                    f"<td>{contribution:.1f}</td>"
                    f"<td>{escape(c.get('what', ''))}</td>"
                    "</tr>"
                )
            st.markdown(
                "<div class='df-sub-table-wrap'><table class='df-domain-table'><thead><tr>"
                "<th>Підкритерій</th><th>Введення</th><th>Тип</th><th>Нормалізований бал</th><th>Вага в домені</th><th>Внесок</th><th>Чому це важливо</th>"
                "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>",
                unsafe_allow_html=True,
            )


def render_fragility_table(criterion_scores: Mapping[str, float], top_n: int = 5) -> None:
    fragility = sorted(CRITERIA, key=lambda c: fragility_index(c, criterion_scores), reverse=True)[:top_n]
    rows = []
    for c in fragility:
        score = safe_score(criterion_scores.get(c["key"], 0)) * 100
        fragility_value = fragility_index(c, criterion_scores) * 100
        chips = "".join([f"<span class='df-risk-chip {kind}'>{escape(label)}</span>" for label, kind in fragility_tags(c, score, fragility_value)])
        rows.append(
            "<tr>"
            f"<td><b>{escape(c['name'])}</b><br>{chips}</td>"
            f"<td>{escape(DOMAIN_BY_KEY[c['domain']]['label'])}</td>"
            f"<td>{score:.1f}</td>"
            f"<td><b>{fragility_value:.1f}</b></td>"
            f"<td>{escape(c.get('what', ''))}</td>"
            f"<td>{escape(fragility_action(c, score))}</td>"
            "</tr>"
        )
    st.markdown(
        "<table class='df-domain-table'><thead><tr>"
        "<th>Точка вразливості</th><th>Домен</th><th>Бал</th><th>Індекс вразливості</th><th>Чому це важливо</th><th>Дія</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>",
        unsafe_allow_html=True,
    )


def render_governance_alerts(vetoes: Sequence[Mapping[str, Any]], gates: Sequence[str]) -> None:
    warnings = st.session_state.get("governance_warnings", [])
    stop_text = "Активних стоп-факторів немає" if not vetoes else "; ".join([f"{v['name']} → {v['signal']}" for v in vetoes])
    gate_items = list(gates) + list(warnings)
    gate_text = "Доменні пороги в нормі" if not gate_items else "; ".join(gate_items)
    review_text = "Перевірити пороги, stop-фактори та слабкі місця"
    rows = [
        ("Стоп-фактори", stop_text, "добре", "good" if not vetoes else "bad"),
        ("Доменні пороги", gate_text, "норма" if not gate_items else "увага", "good" if not gate_items else "warn"),
        ("Тригер перегляду", review_text, "увага", "warn"),
    ]
    html = []
    for label, value, status_label, kind in rows:
        html.append(
            f"<tr><td><b>{escape(label)}</b></td><td>{escape(value)}</td>"
            f"<td><span class='df-risk-chip {kind}'>{escape(status_label)}</span></td></tr>"
        )
    st.markdown(
        "<table class='df-governance-table'><thead><tr><th>Рівень</th><th>Сигнал</th><th>Статус</th></tr></thead><tbody>"
        + "".join(html) + "</tbody></table>",
        unsafe_allow_html=True,
    )


def render_strong_weak_cards(domain_scores: Mapping[str, float], criterion_scores: Mapping[str, float]) -> None:
    weakest_key = min(domain_scores, key=lambda k: domain_scores[k])
    strongest_key = max(domain_scores, key=lambda k: domain_scores[k])
    c1, c2 = st.columns(2)
    with c1:
        _, weak_sub = domain_subcriteria_rank(weakest_key, criterion_scores)
        weak_sub_text = weak_sub["name"] if weak_sub else "—"
        st.markdown(
            f"<div class='df-domain-card-compact'><div class='title'>Найслабший домен</div>"
            f"<div class='score'>{escape(DOMAIN_BY_KEY[weakest_key]['label'])} · {domain_scores[weakest_key]:.1f}</div>"
            f"<div class='body'>Найнижчий підкритерій: {escape(weak_sub_text)}.</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        strong_sub, _ = domain_subcriteria_rank(strongest_key, criterion_scores)
        strong_sub_text = strong_sub["name"] if strong_sub else "—"
        st.markdown(
            f"<div class='df-domain-card-compact'><div class='title'>Найсильніший домен</div>"
            f"<div class='score'>{escape(DOMAIN_BY_KEY[strongest_key]['label'])} · {domain_scores[strongest_key]:.1f}</div>"
            f"<div class='body'>Головна підтримка: {escape(strong_sub_text)}.</div></div>",
            unsafe_allow_html=True,
        )


def render_dashboard_header() -> None:
    """Render the dashboard page header."""
    st.markdown(
        """
        <div class='df-prem-page-head'>
          <div>
            <div class='df-prem-title'>Панель рішення</div>
            <div class='df-prem-meta'>Спочатку підсумок · далі деталізація</div>
          </div>
        </div>
        <div class='df-prem-progress'><div class='df-prem-progress-fill' style='width:100%;'></div></div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_kpi_grid(final: float, status: str, vetoes: Sequence[Mapping[str, Any]], gates: Sequence[str], warnings: Sequence[str]) -> None:
    """Render the top KPI grid on the decision dashboard."""
    completed_total = sum(1 for c in CRITERIA if mcda_criterion_complete(c))
    completion_pct = completed_total / len(CRITERIA) * 100 if CRITERIA else 0.0
    gate_count = len(gates) + len(warnings)
    status_kind = status_visual_kind(status)

    st.markdown("<div class='df-dashboard-grid'>", unsafe_allow_html=True)
    cols = st.columns(5, gap="small")
    with cols[0]:
        render_dashboard_kpi("Підсумковий бал", f"{final:.1f}", score_band_label(final), status_kind)
    with cols[1]:
        render_dashboard_kpi("Статус", status, "фінальний", status_kind)
    with cols[2]:
        render_dashboard_kpi("Стоп-фактори", len(vetoes), "активні" if vetoes else "немає", "bad" if vetoes else "good")
    with cols[3]:
        render_dashboard_kpi("Попередження порогів", gate_count, "потрібен перегляд" if gate_count else "немає", "warn" if gate_count else "good")
    with cols[4]:
        render_dashboard_kpi("Заповнення", f"{completion_pct:.0f}%", f"{completed_total}/{len(CRITERIA)} критеріїв", "good" if completion_pct == 100 else "warn")
    st.markdown("</div>", unsafe_allow_html=True)


def render_dashboard_review_expander(gates: Sequence[str]) -> None:
    """Render the dashboard review-trigger explanation."""
    with st.expander("Деталі тригера перегляду", expanded=False):
        review = "Перед дією потрібен явний перегляд: перевірити доменні пороги, активні стоп-фактори та найвразливіші підкритерії."
        if st.session_state.case_data.get("emotion") in {"overloaded", "stressed", "tired", "excited"}:
            review += " Додатково: повторити оцінку в нейтральному стані через ризик ситуативного шуму."
        if gates:
            review += " Пороги для перегляду: " + ", ".join(gates) + "."
        st.write(review)


def render_counterargument_input() -> None:
    """Render and persist the strongest counterargument field."""
    st.markdown("<div class='df-dash-section-title'>Найсильніший контраргумент</div>", unsafe_allow_html=True)
    ca1, ca2 = st.columns([2.2, 0.8], gap="medium")
    with ca1:
        st.session_state.counterargument = st.text_area(
            "Який найсильніший чесний аргумент проти цього рішення?",
            value=st.session_state.counterargument,
            height=82,
            placeholder="Наприклад: економіка тримається на оптимістичному сценарії; команда ще не довела delivery; рішення забирає забагато уваги.",
        )
    with ca2:
        st.markdown(
            "<div class='df-domain-card-compact'><div class='title'>Підказка</div>"
            "<div class='body'>Напиши найсильніший чесний аргумент проти цього рішення. Не захищай рішення — атакуй його.</div></div>",
            unsafe_allow_html=True,
        )


def render_dashboard_memo_preview(final: float, status: str, domain_scores: ScoreMap, criterion_scores: ScoreMap, gates: Sequence[str]) -> None:
    """Build and render the memo preview expander."""
    memo = build_memo(final, status, domain_scores, criterion_scores, gates)
    st.session_state.memo_markdown = memo
    with st.expander("Попередній перегляд decision memo", expanded=False):
        st.text_area("Мемо", memo, height=260)


def render_dashboard_navigation() -> None:
    """Render dashboard navigation buttons."""
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Назад до MCDA", use_container_width=True):
            go(PAGE_MCDA, len(DOMAINS) - 1)
    with c2:
        if st.button("Експорт мемо", type="primary", use_container_width=True):
            go(PAGE_MEMO)


def page_dashboard() -> None:
    """Render the decision dashboard."""
    render_header()
    render_dashboard_header()

    domain_scores, criterion_scores, final, status, gates = calculate_scores()
    vetoes = active_vetoes()
    warnings = st.session_state.get("governance_warnings", [])

    render_dashboard_kpi_grid(final, status, vetoes, gates, warnings)
    render_recommendation_panel(status, final, vetoes, gates)

    st.markdown("<div class='df-dash-section-title'>Що формує підсумковий бал</div>", unsafe_allow_html=True)
    render_score_explain_table(domain_scores, criterion_scores, final, gates)
    render_strong_weak_cards(domain_scores, criterion_scores)

    with st.expander("Деталі · розклад за підкритеріями", expanded=False):
        render_domain_breakdown_accordion(criterion_scores)

    st.markdown("<div class='df-dash-section-title'>Карта вразливостей</div>", unsafe_allow_html=True)
    render_fragility_table(criterion_scores, top_n=5)

    st.markdown("<div class='df-dash-section-title'>Панель ризиків і контролю</div>", unsafe_allow_html=True)
    render_governance_alerts(vetoes, gates)
    render_dashboard_review_expander(gates)

    render_counterargument_input()
    render_dashboard_memo_preview(final, status, domain_scores, criterion_scores, gates)
    render_dashboard_navigation()


def recommendation_text(final: float, status: str, vetoes: Sequence[Mapping[str, Any]], gates: Sequence[str]) -> str:
    if gates:
        return "Доменний поріг не є veto, але знижує статус на один рівень і вимагає доопрацювання або явного перегляду перед дією."
    if status == "INVEST":
        return "Рішення проходить базову логіку. Перед дією потрібен короткий явний перегляд."
    if status == "HOLD":
        return "Рішення прийнятне, але без великого запасу сили. Рекомендовано утримати позицію або діяти малим розміром після явного перегляду."
    if "REFACTOR" in status:
        return "Рішення має слабкі місця. Потрібно змінити структуру ставки, команду, контроль, часове навантаження або економіку."
    return "Рішення не проходить мінімальний рівень якості. Базова дія — exit / no-go, якщо немає окремого стратегічного аргументу."

def page_memo() -> None:
    render_header()
    render_premium_page_header("Експорт decision memo", "Фінальний текст для збереження або подальшого редагування", progress=100)
    domain_scores, criterion_scores, final, status, gates = calculate_scores()
    memo = build_memo(final, status, domain_scores, criterion_scores, gates)
    st.session_state.memo_markdown = memo

    st.download_button(
        "Завантажити decision memo (.md)",
        data=memo,
        file_name=f"decision_memo_{datetime.now().strftime(MEMO_FILENAME_DATETIME_FORMAT)}.md",
        mime="text/markdown",
        type="primary",
        use_container_width=True,
    )
    st.text_area("Markdown", memo, height=600)
    if st.button("Назад до панелі рішення"):
        go("dashboard")


def memo_options_text(case: Mapping[str, Any]) -> str:
    """Format case options for the decision memo."""
    options = "\n".join([f"- Варіант {chr(65 + i)}: {opt}" for i, opt in enumerate(case.get("options", [])) if opt])
    return options or "- —"


def memo_veto_text(vetoes: Sequence[Mapping[str, Any]]) -> tuple[str, str]:
    """Format active vetoes and veto notes for the decision memo."""
    active_veto_text = "\n".join([f"- {v['name']}: {v['signal']}" for v in vetoes]) or "- немає"
    veto_notes = "\n".join([
        f"- {v['name']}: {st.session_state.veto_notes.get(v['key'], '')}"
        for v in vetoes
        if st.session_state.veto_notes.get(v["key"], "")
    ]) or "- —"
    return active_veto_text, veto_notes


def memo_domain_lines(domain_scores: Mapping[str, float], weights: Mapping[str, float]) -> str:
    """Format domain score and weight lines for the decision memo."""
    return "\n".join([
        f"- {DOMAIN_BY_KEY[k]['label']}: {domain_scores.get(k, 0):.1f} / 100; вага {weights.get(k, 0) * 100:.1f}%"
        for k in [d["key"] for d in DOMAINS]
    ])


def memo_weakest_lines(criterion_scores: Mapping[str, float], weights: Mapping[str, float]) -> str:
    """Format the three weakest weighted criteria for the decision memo."""
    weakest = sorted(
        CRITERIA,
        key=lambda c: weights.get(c["domain"], 0.0) * (1 - criterion_scores[c["key"]]),
        reverse=True,
    )[:3]
    return "\n".join([
        f"- {c['name']} ({DOMAIN_BY_KEY[c['domain']]['label']}): {criterion_scores[c['key']] * 100:.1f} / 100; індекс вразливості {weights.get(c['domain'], 0.0) * (1 - criterion_scores[c['key']]) * 100:.1f}"
        for c in weakest
    ])


def memo_case_section(case: Mapping[str, Any], emotional_warning: str) -> str:
    """Build the memo case section."""
    return f"""## Кейс
Назва: {case.get('title') or '—'}

Контекст:
{case.get('context') or '—'}

Дилема:
{case.get('dilemma') or '—'}

Тип активу / рішення: {case.get('type') or '—'}
Розмір рішення: {case.get('amount', 0):,.0f} {case.get('currency', '')}
Горизонт рішення: {case.get('horizon') or '—'}{emotional_warning}"""


def memo_ahp_section(weights: Mapping[str, float], consistency_ratio: float) -> str:
    """Build the memo AHP weights section."""
    return f"""## AHP-ваги
- Фінанси: {weights.get('economic_quality', 0) * 100:.1f}%
- Стратегія: {weights.get('strategic_significance', 0) * 100:.1f}%
- Керованість: {weights.get('asset_controllability', 0) * 100:.1f}%
- Навантаження: {weights.get('management_load', 0) * 100:.1f}%
- Особиста сумісність: {weights.get('personal_fit', 0) * 100:.1f}%

Consistency Ratio: {consistency_ratio:.3f}"""


def memo_portfolio_section(basket_cfg: Mapping[str, Any]) -> str:
    """Build the memo portfolio role section."""
    return f"""## Роль у портфелі
Кошик: {basket_cfg['label']}
Пороги: {basket_cfg.get('threshold_line', '—')}"""


def memo_stop_factor_section(active_veto_text: str, veto_notes: str) -> str:
    """Build the memo stop-factor section."""
    return f"""## Stop-фактори
Виявлені стоп-фактори:
{active_veto_text}

Примітка: стоп-фактори не скасовують MCDA-бал. Рішення залишається за власником.

Нотатки:
{veto_notes}"""


def memo_mcda_section(final: float, status: str, gates_text: str, governance_warnings_text: str) -> str:
    """Build the memo MCDA summary section."""
    return f"""## MCDA-бали
Підсумковий бал: {final:.1f} / 100
Статус рішення: {status}

Доменні пороги:
{gates_text}

Попередження governance:
{governance_warnings_text}"""


def memo_review_section(counterargument: str, final: float, status: str, vetoes: Sequence[Mapping[str, Any]], gates: Sequence[str]) -> str:
    """Build the memo review and final recommendation section."""
    return f"""## Найсильніший контраргумент
{counterargument}


## Тригер перегляду
Перед дією потрібен явний перегляд: перевірити доменні пороги, активні стоп-фактори та найвразливіші підкритерії.

## Фінальна рекомендація
{recommendation_text(final, status, vetoes, gates)}"""


def build_memo(final: float, status: str, domain_scores: ScoreMap, criterion_scores: ScoreMap, gates: Sequence[str]) -> str:
    """Build the Markdown decision memo from current session state and calculated scores."""
    case = st.session_state.case_data
    weights = st.session_state.ahp_weights
    cr = st.session_state.consistency_ratio
    vetoes = active_vetoes()
    basket = st.session_state.get("portfolio_basket") or DEFAULT_BASKET_KEY
    basket_cfg = BASKET_CONFIG[basket]

    options = memo_options_text(case)
    active_veto_text, veto_notes = memo_veto_text(vetoes)
    domain_lines = memo_domain_lines(domain_scores, weights)
    weakest_lines = memo_weakest_lines(criterion_scores, weights)
    counterargument = st.session_state.counterargument.strip() or DEFAULT_MEMO_COUNTERARGUMENT

    emotional_warning = "\n" + EMOTION_MEMO_NOTES.get(case.get("emotion", "calm"), "Поточний стан не вказано.")
    gates_text = "\n".join([f"- {g}" for g in gates]) or "- немає"
    governance_warnings = st.session_state.get("governance_warnings", [])
    governance_warnings_text = "\n".join([f"- {w}" for w in governance_warnings]) or "- немає"

    return "\n\n".join([
        "# Decision memo",
        f"Створено: {datetime.now().strftime(MEMO_DATETIME_FORMAT)}",
        memo_case_section(case, emotional_warning),
        "## Варіанти\n" + options,
        memo_ahp_section(weights, cr),
        memo_portfolio_section(basket_cfg),
        memo_stop_factor_section(active_veto_text, veto_notes),
        memo_mcda_section(final, status, gates_text, governance_warnings_text),
        "## Бали доменів\n" + domain_lines,
        "## Найвразливіші місця\n" + weakest_lines,
        memo_review_section(counterargument, final, status, vetoes, gates),
    ]) + "\n"

def normalize_page_key(page: Any) -> str:
    """Normalize current page key and migrate legacy values."""
    if page == LEGACY_PAGE_CASE:
        st.session_state.current_step = PAGE_AHP
        return PAGE_AHP
    if page in PAGE_KEYS:
        return str(page)
    return PAGE_WELCOME


SCROLL_TO_TOP_SCRIPT = """
        <script>
        (function () {
          const doc = window.parent.document;

          function scrollOne(target) {
            if (!target) return;
            try { target.scrollTo({ top: 0, left: 0, behavior: 'auto' }); } catch (e) {}
            try { target.scrollTop = 0; } catch (e) {}
            try { target.pageYOffset = 0; } catch (e) {}
          }

          function scrollTop() {
            const fixedTargets = [
              window.parent,
              doc.scrollingElement,
              doc.documentElement,
              doc.body,
              doc.querySelector('[data-testid="stAppViewContainer"]'),
              doc.querySelector('[data-testid="stApp"]'),
              doc.querySelector('[data-testid="stVerticalBlock"]'),
              doc.querySelector('section.main'),
              doc.querySelector('.main')
            ].filter(Boolean);

            fixedTargets.forEach(scrollOne);

            Array.from(doc.querySelectorAll('*')).forEach((el) => {
              try {
                const style = window.parent.getComputedStyle(el);
                const canScroll = /(auto|scroll|overlay)/.test(style.overflowY + style.overflow);
                if (canScroll || el.scrollHeight > el.clientHeight + 8) {
                  el.scrollTop = 0;
                }
              } catch (e) {}
            });
          }

          scrollTop();
          window.parent.requestAnimationFrame(scrollTop);
          setTimeout(scrollTop, 50);
          setTimeout(scrollTop, 120);
          setTimeout(scrollTop, 300);
          setTimeout(scrollTop, 700);
          setTimeout(scrollTop, 1200);
        })();
        </script>
        """


def render_scroll_to_top_script() -> None:
    """Mount the JavaScript snippet that resets Streamlit scroll containers."""
    components.html(
        SCROLL_TO_TOP_SCRIPT,
        height=SCROLL_COMPONENT_SIZE,
        width=SCROLL_COMPONENT_SIZE,
    )


def scroll_to_top_if_requested() -> None:
    """Scroll the app viewport to top after page/domain navigation."""
    if not st.session_state.get("scroll_to_top", False):
        return
    st.session_state.scroll_to_top = False
    render_scroll_to_top_script()

def render_page(page: str) -> None:
    """Dispatch the current wizard page to the matching renderer."""
    page_renderers = {
        PAGE_WELCOME: page_welcome,
        PAGE_AHP: page_ahp,
        PAGE_BASKET: page_basket,
        PAGE_VETO: page_veto,
        PAGE_MCDA: page_mcda,
        PAGE_DASHBOARD: page_dashboard,
        PAGE_MEMO: page_memo,
    }
    page_renderers.get(page, page_welcome)()
    # Render the scroll script after the target page is mounted; otherwise
    # Streamlit may restore the old scroll position during the rerender.
    scroll_to_top_if_requested()


def main() -> None:
    """Run the Streamlit decision framework application."""
    init_state()
    sync_ahp_answers_from_widgets()
    calculate_ahp()
    render_sidebar()
    render_page(normalize_page_key(st.session_state.current_step))


if __name__ == "__main__":
    main()
