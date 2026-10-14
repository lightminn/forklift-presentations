"""Build the week 7 UOS web deck and its Korean speaker script.

Run from any directory with Python 3. No third-party build dependencies.

Week 7 (class, 2026-10-14) is hardware only (user, 2026-10-14): the power and
control layout (redrawn from the team's diagram.png), the motor and encoder
boards the team drew in EasyEDA -- the motor board (schematic page 1 of 3,
"MOTOR&SENSOR"), the MT6701 wheel encoder board (MT_DS V1.0.0), the KTH7801
absolute encoder board (KTH_Enc V1.1.2) and the STDS board that carries the
KTH7801's SPI over LVDS (V1.0.0) -- why the encoder lines are differential, the
clock and cable-delay budget, power and connectors, and the connector-pitch
question for the professor. The figures are cut from the team's exports by
prepare_figures.py; every chip figure is from its datasheet (SOURCES.md).
The multi-forklift traffic slides that were here until 99fc8b1 are dropped.
"""
from html import escape
from pathlib import Path
import json
from hashlib import sha256

ROOT = Path(__file__).resolve().parent
slides = []

BLUE, LIGHT, GREY, RED = '#2f74c0', '#9cc3ea', '#9aa3ad', '#c0392b'
P12, P5, P33 = '#d64541', '#e08a1e', '#1e9e6a'      # 12 V, 5 V, 3.3 V lines in the system diagram

# datasheets and references (SOURCES.md lists versions)
DS_DRV = 'https://www.ti.com/lit/ds/symlink/drv8244-q1.pdf'
DS_MT = 'https://uploadcdn.oneyac.com/attachments/files/brand_pdf/magntek/F3/CA/MT6701QT-STD.pdf'
DS_MT_CN = 'https://atta.szlcsc.com/upload/public/pdf/source/20260616/FEB700C1922508565884FF0A90656B50.pdf'
DS_KTH = 'https://shop.mev-elektronik.com/wp-content/uploads/KTH7801_datasheet_EN.pdf'
DS_LVDS31 = 'https://www.ti.com/lit/ds/symlink/sn65lvds31.pdf'
DS_LVDS32 = 'https://www.ti.com/lit/ds/symlink/sn65lvds32.pdf'
DS_LVDS1 = 'https://www.ti.com/lit/ds/symlink/sn65lvds1.pdf'
DS_LVC125 = 'https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf'
DS_AM26 = 'https://www.ti.com/lit/ds/symlink/am26lv32.pdf'
DS_LDO = 'https://www.ti.com/lit/ds/symlink/tlv702.pdf'
DS_LTC4332 = 'https://www.analog.com/en/products/ltc4332.html'
TIDA = 'https://www.ti.com/lit/ug/tidued8/tidued8.pdf'
TEAM = '팀 EasyEDA 자료 (2026-10-14)'
MAIN = f'{TEAM} mainboard_1.png'


def add(label, title, seconds, body, notes, sources, foot):
    slides.append(dict(label=label, title=title, seconds=seconds, body=body,
                       notes=notes, sources=sources, foot=foot))


def img(src, alt, cap=None, cls='shot'):
    c = f'<figcaption>{cap}</figcaption>' if cap else ''
    return (f'<figure class="{cls}"><img class="media" src="assets/{src}" '
            f'alt="{escape(alt, quote=True)}">{c}</figure>')


def r3d(src, alt, cap=None):
    return img(src, alt, cap, 'shot r3d')


def sch(src, alt, cap=None):
    return img(src, alt, cap, 'shot sch')


def table(head, rows, cls='comparison h7'):
    h = ''.join(f'<th>{x}</th>' for x in head)
    body = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in r) + '</tr>' for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{body}</table>'


def lgd(*items):
    """Legend for the light charts: (kind, colour, text), kind box / line / dash / x."""
    out = []
    for kind, colour, text in items:
        if kind == 'x':
            sw = f'<span class="sw x" style="color:{colour}">×</span>'
        elif kind == 'dash':
            sw = f'<span class="sw dash" style="border-color:{colour}"></span>'
        elif kind == 'line':
            sw = f'<span class="sw ln" style="background:{colour}"></span>'
        else:
            sw = f'<span class="sw" style="background:{colour}"></span>'
        out.append(f'<span class="lg">{sw}{text}</span>')
    return f'<div class="lgd7">{"".join(out)}</div>'


# ----------------------------------------------------------------- numbers
# SPI over LVDS noise test, TI TIDUED8 Table 4 (1 Vpp noise coupled, CAT5 cable)
NOISE = ['없음', '10 kHz', '100 kHz', '500 kHz', '1 MHz', '5 MHz', '10 MHz']
SE_05 = [101, 99, 82, 67, 58, 39, 31]
LV_05 = [101, 99, 83, 69, 68, 61, 52]
LV_3 = [101, 97, 71, 67, 59, 49, 45]          # single-ended at 3 m: "Fail" in every row
SHOW = [0, 2, 4, 6]       # rows drawn on the slide (user: fewer frequencies): none, 100 kHz, 1 MHz, 10 MHz

V_CABLE = 20.0          # cm/ns, twisted pair (about 2/3 of light speed)
# worst-case (max) delays on the MISO round trip, ns, each from its datasheet
DELAYS = [('메인보드 LVDS 송신 (SN65LVDS31)', 2.5),
          ('STDS LVDS 수신 (SN65LVDS32)', 3.0),
          ('KTH7801 MISO 출력', 50.0),
          ('STDS LVDS 송신 (SN65LVDS1)', 3.1),
          ('메인보드 LVDS 수신 (SN65LVDS32)', 3.0),
          ('MISO 버퍼 (SN74LVC1G125)', 3.7)]
CHIP_NS = sum(d for _, d in DELAYS)           # 65.3 ns


def f_max(length_m):
    """Largest SCLK (MHz) for which MISO is back within half a period (CPHA = 1)."""
    return 1000.0 / (2 * (CHIP_NS + 2 * length_m * 100 / V_CABLE))


LENGTHS = [0, 1, 2, 3, 5]


# ----------------------------------------------------------------- figures
def system_diagram():
    """Power and control layout, redrawn from the team's diagram.png in the deck's style."""
    boxes = [(10, 178, 180, 116, '12 V 배터리', '차량 주 전원'),
             (262, 46, 256, 84, '12 V → 5 V 벅 컨버터', 'MCU와 센서 보드 전원'),
             (902, 46, 262, 84, '5 V → 3.3 V LDO', '센서 보드마다 (TLV70233)'),
             (262, 182, 256, 84, 'Nucleo STM32H533RE', 'Cortex-M33, 3.3 V 입출력'),
             (902, 182, 262, 84, '엔코더 4개 (자기식)', 'MT6701 × 2, KTH7801 × 2'),
             (262, 352, 256, 84, 'DRV8244 × 4', 'H 브리지, 전류 감지 내장'),
             (902, 352, 262, 84, '모터 4개 (12 V)', '바퀴 L · R, 조향, 승강')]
    lines = [((190, 212), (224, 212), (224, 88), (260, 88)), P12, False, None,
             ((190, 262), (224, 262), (224, 394), (260, 394)), P12, False, None,
             ((518, 88), (900, 88)), P5, False, ('5 V (케이블로)', 709, 76),
             ((390, 130), (390, 180)), P5, False, ('5 V', 402, 162),
             ((1033, 130), (1033, 180)), P33, False, ('3.3 V', 1045, 162),
             ((900, 224), (520, 224)), BLUE, True, ('ABZ (바퀴), SPI (조향 · 승강)', 709, 212),
             ((390, 266), (390, 350)), BLUE, True, ('PWM, 방향, SPI, DRVOFF', 402, 307),
             ((518, 394), (900, 394)), P12, False, ('OUT1, OUT2', 709, 382)]
    parts = ['<defs>' + ''.join(
        f'<marker id="ah{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for c in (P12, P5, P33, BLUE)) + '</defs>']
    for x, y, w, h, label in ((236, 10, 938, 276, '제어와 센서 전원'), (236, 316, 938, 142, '모터 구동 전원')):
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f7f9fb" stroke="#c3cad3" stroke-width="2" stroke-dasharray="8 6"/>'
                     f'<text x="{x + 16}" y="{y + 26}" font-size="17" font-weight="700" fill="#5d6670">{label}</text>')
    for i in range(0, len(lines), 4):
        pts, col, dashed, lab = lines[i:i + 4]
        d = ' '.join(f'{x},{y}' for x, y in pts)
        dash = ' stroke-dasharray="10 7"' if dashed else ''
        parts.append(f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="4"{dash} marker-end="url(#ah{col[1:]})"/>')
        if lab:
            t, tx, ty = lab
            anchor = 'start' if pts[0][0] == pts[-1][0] else 'middle'
            parts.append(f'<text x="{tx}" y="{ty}" text-anchor="{anchor}" font-size="17" font-weight="700" fill="{col}">{t}</text>')
    for x, y, w, h, t, s in boxes:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#fff" stroke="{BLUE if "STM32" in t else "#8c97a3"}" stroke-width="{3 if "STM32" in t else 2}"/>'
                     f'<text x="{x + w / 2}" y="{y + h / 2 - 4}" text-anchor="middle" font-size="21" font-weight="700" fill="#1b1f24">{t}</text>'
                     f'<text x="{x + w / 2}" y="{y + h / 2 + 22}" text-anchor="middle" font-size="16" fill="#5d6670">{s}</text>')
    return ('<svg class="diagram" viewBox="0 0 1180 462" role="img" aria-label="전원 계통과 제어 구성. 12 V 배터리가 벅 컨버터와 DRV8244 네 개에 12 V를 주고, '
            '벅 컨버터의 5 V가 MCU와 센서 보드의 LDO로, LDO의 3.3 V가 엔코더 네 개로 간다. 엔코더는 ABZ와 SPI로 MCU에, MCU는 PWM, 방향, SPI, DRVOFF로 드라이버에, 드라이버는 모터 네 개에 연결된다">'
            f'<g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


def snr_chart():
    W, H, L, B, T = 1000, 380, 64, 330, 18
    ymax = 110
    gw = (W - L - 10) / len(SHOW)
    bw = gw / 5.6
    y = lambda v: B - v / ymax * (B - T)
    parts = []
    for v in (0, 20, 40, 60, 80, 100):
        parts.append(f'<line x1="{L}" x2="{W - 10}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#e3e7ec"/>'
                     f'<text x="{L - 10}" y="{y(v) + 6:.1f}" text-anchor="end" font-size="17" fill="#44505c">{v}</text>')
    for i, k in enumerate(SHOW):
        name = NOISE[k]
        x0 = L + i * gw + gw * 0.08
        for j, (vals, col) in enumerate(((SE_05, GREY), (LV_05, LIGHT), (None, RED), (LV_3, BLUE))):
            x = x0 + j * bw * 1.08
            if vals is None:
                parts.append(f'<text x="{x + bw / 2:.1f}" y="{B - 8}" text-anchor="middle" font-size="26" font-weight="700" fill="{RED}">×</text>')
                continue
            v = vals[k]
            parts.append(f'<rect x="{x:.1f}" y="{y(v):.1f}" width="{bw:.1f}" height="{B - y(v):.1f}" fill="{col}"/>')
            if j in (0, 3):
                parts.append(f'<text x="{x + bw / 2:.1f}" y="{y(v) - 6:.1f}" text-anchor="middle" font-size="20" fill="#1b1f24">{v}</text>')
        parts.append(f'<text x="{L + i * gw + gw / 2:.1f}" y="{B + 32}" text-anchor="middle" font-size="22" fill="#1b1f24">{name}</text>')
    parts.append(f'<text x="14" y="{T + 2}" font-size="16" fill="#44505c">dB</text>')
    return (f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="잡음 주파수별 SPI 신호 대 잡음비. '
            f'단일 종단 0.5 m는 101에서 31 dB로, LVDS 0.5 m는 101에서 52 dB로 내려가고, 3 m에서 단일 종단은 모두 실패, LVDS는 101에서 45 dB">'
            f'<g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


def elen_chart():
    W, H, L, B, T, R = 760, 400, 70, 340, 16, 20
    xmax, ymax = 4.0, 0.75
    x = lambda m: L + m / xmax * (W - L - R)
    y = lambda e: B - e / ymax * (B - T)
    parts = []
    for e in (0, 0.2, 0.4, 0.6):
        parts.append(f'<line x1="{L}" x2="{W - R}" y1="{y(e):.1f}" y2="{y(e):.1f}" stroke="#e3e7ec"/>'
                     f'<text x="{L - 10}" y="{y(e) + 6:.1f}" text-anchor="end" font-size="17" fill="#44505c">{e:.1f}</text>')
    for m in range(5):
        parts.append(f'<text x="{x(m):.1f}" y="{B + 28}" text-anchor="middle" font-size="17" fill="#44505c">{m} m</text>')
    parts.append(f'<line x1="{L}" x2="{W - R}" y1="{y(0.1):.1f}" y2="{y(0.1):.1f}" stroke="{RED}" stroke-width="3" stroke-dasharray="9 6"/>')
    for f_mhz, col in ((5, LIGHT), (10, BLUE), (35, '#1b3f6b')):
        k = f_mhz * 1e6 / (V_CABLE * 1e7)        # electrical length per metre
        m_end = min(xmax, ymax / k)
        parts.append(f'<line x1="{x(0):.1f}" y1="{y(0):.1f}" x2="{x(m_end):.1f}" y2="{y(k * m_end):.1f}" stroke="{col}" stroke-width="4"/>')
        cross = 0.1 / k
        if cross <= xmax:
            parts.append(f'<circle cx="{x(cross):.1f}" cy="{y(0.1):.1f}" r="7" fill="#fff" stroke="{col}" stroke-width="3"/>'
                         f'<text x="{x(cross) - 10:.1f}" y="{y(0.1) - 14:.1f}" text-anchor="end" font-size="18" font-weight="700" fill="{col}">{cross:.1f} m</text>')
    return (f'<svg class="diagram" viewBox="0 0 {W} {H}" role="img" aria-label="케이블 길이에 따른 전기적 길이. 0.1 기준선을 5 MHz는 4 m, 10 MHz는 2 m, 35 MHz는 약 0.6 m에서 넘음">'
            f'<g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


def fmax_chart():
    left, width, row = 150, 330, 66
    parts = []
    for i, m in enumerate(LENGTHS):
        v = f_max(m)
        yy = 34 + i * row
        w = v / 8.0 * width
        name = '케이블 없음' if m == 0 else f'{m} m'
        parts.append(f'<text x="{left - 12}" y="{yy + 8}" text-anchor="end" font-size="22" fill="#1b1f24">{name}</text>'
                     f'<rect x="{left}" y="{yy - 21}" width="{w:.1f}" height="42" rx="3" fill="{BLUE if m == 3 else LIGHT}"/>'
                     f'<text x="{left + w + 12:.1f}" y="{yy + 10}" font-size="26" font-weight="700" fill="#1b1f24">{v:.1f} MHz</text>')
    return (f'<svg class="diagram" viewBox="0 0 640 {10 + row * len(LENGTHS)}" role="img" aria-label="케이블 길이별 최대 SCLK. '
            + ', '.join(f'{m} m {f_max(m):.1f} MHz' for m in LENGTHS) + '">'
            f'<g font-family="var(--uos-font)">{"".join(parts)}</g></svg>')


# ----------------------------------------------------------------- 1
add('개발 진행 보고', '7주차\n자율 지게차 개발', 25, '',
    """안녕하십니까. 7주차 자율 지게차 개발 진행 상황을 발표할 김광민이라고 합니다. 이번 주에는 하드웨어만 다루겠습니다. 전원과 제어 구성을 먼저 보이고, 모터 드라이버와 엔코더를 MCU에 잇는 보드 네 종류의 회로와 PCB, 엔코더 신호를 케이블로 멀리 보내기 위해 차동 전송을 고른 근거와 클럭 속도 계산, 전원과 커넥터를 말씀드린 뒤, 결론과 향후 작업으로 마치겠습니다. (전환)""",
    [(TEAM, 'diagram · mainboard_1 · mt6701_1–3 · kth7801_1–3 · stds_1–3')], '진행 보고')


# ----------------------------------------------------------------- 2
add('전원과 제어 구성', '01  전원과 제어 구성', 55, f"""
<h2 class="headline">12 V 배터리에서 모터는 바로, MCU와 센서는 5 V와 3.3 V로 낮춰 공급</h2>
<div class="chart7 sys7 grow">
{system_diagram()}
{lgd(('line', P12, '12 V 주 전원'), ('line', P5, '5 V (벅 컨버터)'), ('line', P33, '3.3 V (LDO)'), ('dash', BLUE, '제어와 피드백 신호'))}
</div>
<div class="takeaway">모터 구동 전원과 제어 · 센서 전원을 나누고, 센서 전원은 LDO를 한 번 더 거쳐 잡음이 적은 3.3 V로 받습니다</div>
""",
    """전체 전원과 제어 구성입니다. 차량의 주 전원은 12볼트 배터리입니다. 아래쪽 모터 구동 전원은 12볼트를 그대로 DRV8244 네 개에 넣고, 드라이버가 바퀴 두 개와 조향, 승강 모터를 구동합니다. 위쪽 제어와 센서 전원은 먼저 벅 컨버터로 12볼트를 5볼트로 낮춰 MCU 보드인 Nucleo STM32H533RE에 주고, 같은 5볼트를 케이블로 센서 보드까지 보내 각 보드의 LDO에서 3.3볼트로 한 번 더 낮춥니다. 엔코더 네 개는 모두 자석의 회전을 재는 자기식이고, 바퀴는 ABZ 펄스, 조향과 승강은 SPI로 MCU에 각도를 알려 줍니다. MCU는 PWM과 방향 신호, SPI 설정, 출력 차단 신호로 드라이버를 제어합니다. (전환)""",
    [(f'{TEAM} diagram.png', '기계차 전력 계통 및 제어 블록 다이어그램 — 12 V 배터리, 12 V → 5 V 벅, 5 V → 3.3 V LDO, Nucleo STM32H533RE, 엔코더 MT6701 · KTH7801, DRV8244/DRV8245, 구동 · 조향 모터'),
     ('다시 그리며 고친 곳', '「TKH7801」→ KTH7801; KTH7801은 광학식이 아니라 홀 소자 자기식 (KTH7801 데이터시트 「Hall magnetic encoders」); 피드백에서 PWM 제외 (두 보드 모두 PWM 핀 미사용); 드라이버는 회로도대로 DRV8244 × 4; 모터에 승강 추가 (채널 H)'),
     (MAIN, 'DRV8244SQRYJRQ1 × 4 (L · R · M · H), 커넥터 5V 공급'),
     (DS_KTH, '「16-bit Programmable non-contact Hall magnetic encoders」')],
    '그림: 팀 블록 다이어그램을 이 덱의 배치와 색으로 다시 그림')

# ----------------------------------------------------------------- 3
add('보드 구성과 신호 경로', '02  보드 구성과 신호 경로', 55, f"""
<h2 class="headline">바퀴는 증분 펄스를 차동 신호로, 조향 · 승강은 SPI를 LVDS로 전송</h2>
<div class="hw7 sch3 grow">
{sch('83_main_sch.png', '메인보드 회로도 1쪽 MOTOR&SENSOR 전체. 위와 왼쪽 아래에 DRV8244 네 개, 가운데 AM26LV32 두 개와 1.27 mm 커넥터 두 개, 오른쪽에 SN74LVC1G125 두 개, SN65LVDS31 두 개, SN65LVDS32 한 개, 아래 RJ 잭 두 개')}
<table class="comparison h7 vt7"><tr><th>신호 경로</th></tr>
<tr><td><b>바퀴 L, R</b><br>MT6701 증분 → 차동 펄스</td></tr>
<tr><td><b>조향, 승강</b><br>KTH7801 SPI → STDS → LVDS</td></tr>
<tr><td><b>전원</b><br>5 V → LDO 3.3 V</td></tr></table>
</div>
<div class="takeaway">바퀴 엔코더는 회전 펄스를, 조향과 승강 엔코더는 SPI로 각도 값을 보내므로 신호 종류에 맞는 차동 방식을 씁니다</div>
""",
    """보드 사이의 연결입니다. 왼쪽은 메인보드 회로도입니다. 바퀴 두 개에 단 MT6701 보드는 1.27밀리미터 2열 4핀 케이블로 메인보드에 바로 이어지고, 증분형 엔코더의 A, B, Z 펄스를 반전 신호와 함께 차동으로 보내고, 메인보드의 차동 수신기 AM26LV32가 받아 MCU 타이머의 엔코더 모드로 셉니다. 차동 수신기는 두 선의 전압 차이만 보므로, 모터 잡음처럼 두 선에 똑같이 실린 잡음은 빼기에서 사라집니다. 조향과 승강에 단 KTH7801 보드는 SPI로 각도 값을 내보내는데, SPI는 원래 한 보드 안에서 쓰는 단일 종단 신호라 먼 거리를 못 갑니다. 그래서 바로 옆에 STDS 보드를 두어 SPI 네 선을 LVDS 차동 신호로 바꾸고, RJ50 케이블로 메인보드에 보냅니다. 메인보드는 SN65LVDS31로 클럭과 데이터를 보내고 SN65LVDS32로 돌아오는 데이터를 받습니다. 전원은 모든 케이블에 5볼트로 실어 보내고 센서 쪽 보드에서 3.3볼트로 낮춥니다. (전환)""",
    [(MAIN, 'DRV8244SQRYJRQ1 × 4 (L · R · M · H 신호 이름), AM26LV32EIPWR U3 · U5, HX JN1.27-2x4P CN1 · CN2 (5 V · AGND · L/R_DA · DB · DZ와 반전), SN74LVC1G125DBVR U9 · U10, SN65LVDS31DR U6 · U7, SN65LVDS32DR U8, 5558067-1 RJ1 · RJ2'),
     (f'{TEAM} mt6701_3 · kth7801_3 · stds_1', '센서 쪽 TLV70233DBVR (VCC → 3V3), CN1 HX JN1.27-2x4P, STDS RJ1 5558067-1'),
     ('사용자 (2026-10-14)', '차동 신호 기반 통신, 5 V로 보내 3.3 V LDO로 강하, RJ50 선택')],
    '그림: 팀 메인보드 회로도 1쪽 (바깥 좌표 띠만 잘라 냄)')

# ----------------------------------------------------------------- 4
add('모터 드라이버 4채널', '03  모터 드라이버 4채널', 50, f"""
<h2 class="headline">DRV8244 네 개가 SPI 선을 함께 쓰고 CS와 방향 입력만 채널마다 따로 받음</h2>
<div class="hw7 grow">
{sch('83_main_drv.png', 'DRV8244SQRYJRQ1 L 채널 회로. nFAULT, IPROPI, nSLEEP, VM, OUT1, OUT2, SDO, SDI, SCLK, nSCS, PH/IN2, EN/IN1, DRVOFF 핀과 주변 저항, 커패시터', '모터 드라이버 회로도')}
<div class="stack">
{table(['채널', '구동'], [('L, R', '왼쪽, 오른쪽 바퀴'), ('M', '조향'), ('H', '승강')])}
{table(['신호', '역할'], [
    ('MISO, MOSI, CLK', '네 채널 공유 (설정과 결함 확인)'),
    ('CS', '채널마다 따로 (2.2 kΩ 풀업)'),
    ('IN1, IN2', '방향과 속도 (PWM)'),
    ('DRVOFF', '출력 즉시 차단'),
    ('nSLEEP, nFAULT', '대기 전환, 결함 알림'),
    ('IPROPI', '모터 전류를 전압으로 (ADC)')])}
</div>
</div>
<div class="takeaway">설정과 진단은 SPI 한 묶음으로 하고, 출력 차단(DRVOFF)은 비상정지와 연결합니다</div>
""",
    """모터 드라이버입니다. 지난번 초안은 세 채널이었는데, 바퀴를 왼쪽과 오른쪽으로 나눠 L, R, 조향 M, 승강 H의 네 채널로 늘렸습니다. 드라이버는 5주차에 고른 TI의 DRV8244 SPI형이고, 왼쪽 회로가 그중 L 채널입니다. 네 채널은 회로가 같고, 설정과 결함 확인에 쓰는 SPI의 MISO, MOSI, 클럭은 네 개가 함께 쓰며 칩 선택 CS만 채널마다 따로 둡니다. 모터의 방향과 속도는 IN1, IN2에 PWM을 넣어 정하고, DRVOFF 핀은 출력을 바로 끊는 핀이라 비상정지와 연결합니다. nFAULT로 결함을 알리고, IPROPI 핀으로 모터 전류를 전압으로 바꿔 MCU의 ADC로 읽습니다. (전환)""",
    [(MAIN, 'DRV8244SQRYJRQ1 × 4: 공유 MISO · MOSI · CLK, 채널별 x_CS(2.2 kΩ 풀업) · x_IN1 · x_IN2 · x_DRVOFF · x_SLEEP · x_FAULT(2.2 kΩ 풀업) · x_IPROPI(10 nF), VM 10 µF + 100 nF'),
     ('사용자 (2026-10-14)', '채널 L · R 바퀴, M 조향, H 승강'),
     (DS_DRV, 'DRV8244-Q1 SLVSG24C — SPI 설정 · 진단, DRVOFF, IPROPI 전류 출력'),
     ('week-07-1 15쪽', 'DRVOFF를 무선 비상정지와 연동할 예정')],
    '그림: 팀 메인보드 회로도 1쪽에서 L 채널만 잘라 냄')

# ----------------------------------------------------------------- 5
add('엔코더 배치와 칩 선정', '04  엔코더 배치와 칩 선정', 55, f"""
<h2 class="headline">바퀴는 MT6701 증분 엔코더, 조향과 승강은 KTH7801 절대 엔코더</h2>
<div class="hw7 grow">
<div class="stack">
{r3d('80_mt_top.jpg', 'MT6701 보드 3D 앞면. QFN-16 칩 U1, C1, C3, 2열 4핀 단자', 'MT6701 보드 (바퀴 L, R)')}
{r3d('81_kth_top.jpg', 'KTH7801 보드 3D 앞면. SOP-8 칩 U2, R4, C1, C2와 2열 4핀 단자', 'KTH7801 보드 (조향 M, 승강 H)')}
</div>
{table(['항목', 'MT6701', 'KTH7801'], [
    ('출력', 'A, B, Z 펄스 (증분)', 'SPI 각도 값 (절대)'),
    ('분해능', '1,024펄스/회전', '12비트 + CRC 4비트'),
    ('비선형 오차', '±1.0° (대표값)', '<b>±0.35°</b> (대표값)'),
    ('전원 켤 때', '회전 수부터 셈', '<b>바로 현재 각도</b>'),
    ('패키지', 'QFN-16', 'SOP-8'),
    ('품번', 'MT6701QT-ACD', 'KTH7801-X-C-SOP8')], 'comparison h7 nwall')}
</div>
<div class="takeaway">바퀴는 회전 펄스를 세면 되지만, 조향과 승강은 전원을 켜자마자 현재 각도를 알아야 해서 절대 엔코더를 씁니다</div>
""",
    """엔코더 배치입니다. 5주차에는 MT6701 한 칩으로 증분과 절대를 모두 하려 했는데, 절대 엔코더는 KTH7801로 바꿨습니다. 바퀴 두 개에는 MT6701을 달아 한 바퀴에 1,024개 나오는 A, B 펄스를 MCU 타이머로 세어 속도와 이동 거리를 잽니다. 조향과 승강에는 KTH7801을 다는데, 전원을 켜자마자 현재 각도를 SPI로 읽을 수 있어 원점을 찾는 동작이 필요 없습니다. 데이터시트의 비선형 오차 대표값은 MT6701이 ±1도, KTH7801이 ±0.35도로, 조향각처럼 각도 값 자체를 쓰는 곳에 KTH7801이 더 맞습니다. 쓰는 KTH7801 품번은 CRC가 붙는 판이라, SPI로 읽을 때 12비트 각도와 4비트 검사값이 함께 옵니다. (전환)""",
    [('사용자 (2026-10-14)', '「absolute는 KTH7801 이거쓸거임」, MT6701 · KTH7801 보드 구별'),
     (DS_MT, 'MT6701 Rev.1.5 — INL ±1.0° 대표 · ±1.5° 최대, 14비트, ABZ 1–1024 PPR'),
     (DS_MT_CN, 'MT6701 1.9판(2024-05) 주문 정보 — MT6701QT-ACD: AB 1,024펄스/회전, Z 1 LSB, UVW = -A-B-Z'),
     (DS_KTH, 'KTH7801 Series (2024-09-27) — 절대각 16비트(N 판), C 판(KTH7801-X-C-SOP8, 사용 품번)은 SPI 한 프레임이 각도 12비트 + CRC 4비트 (사용자 확인 2026-10-14), 비선형 오차 ±0.35°(대표), SOP-8 = SPI · PWM, KTH7801-X-C-SOP8 = CRC 판, 5.6절 SPI CRC 프레임 12비트 각도 + CRC-4'),
     ('week-05/build_deck.py 6쪽', '5주차 엔코더 선정: MT6701로 증분 · 절대 모두')],
    '그림: 팀 3D 렌더')

# ----------------------------------------------------------------- 6
add('엔코더 보드 두 종', '05  엔코더 보드 두 종', 60, f"""
<h2 class="headline">엔코더 보드는 칩과 LDO만 두고 1.27 mm 2×4 커넥터로 신호와 5 V를 주고받음</h2>
<div class="enc7 grow">
{sch('80_mt_sch.png', 'MT6701 보드 회로도. MT6701QT-ACD U1의 A, B, Z 핀과 U, V, W 핀을 반전 A, B, Z로, TLV70233 U2가 VCC를 3V3으로, CN1 HX JN1.27-2x4P', 'MT6701 보드 회로도 (MT_DS V1.0.0)')}
{sch('81_kth_sch.png', 'KTH7801 보드 회로도. KTH7801-X-C-SOP8 U2의 MOSI, CS, MISO, SCLK, CS에 2.2 kΩ 풀업 R4, TLV70233 U1, CN1 HX JN1.27-2x4P', 'KTH7801 보드 회로도 (KTH_Enc V1.1.2)')}
</div>
<table class="comparison h7 nwall enc7t"><tr><th></th><th>MT6701 보드 (바퀴)</th><th>KTH7801 보드 (조향 · 승강)</th></tr>
<tr><td>보내는 값</td><td>바퀴가 돈 만큼 나오는 펄스</td><td>지금 각도 (숫자 값)</td></tr>
<tr><td>신호 선</td><td>펄스 3쌍 (A, B, Z와 반전)</td><td>SPI 4선 (CS, CLK, MOSI, MISO)</td></tr>
<tr><td>전원</td><td colspan="2">케이블로 5 V를 받아 보드에서 3.3 V로 낮춤</td></tr></table>
""",
    """엔코더 보드 두 종류의 회로도입니다. 왼쪽은 바퀴에 다는 MT6701 보드입니다. 칩은 QFN 패키지의 MT6701QT-ACD인데, 이 품번은 공장에서 U, V, W 핀이 A, B, Z의 반전 신호를 내도록 설정되어 나오므로, 따로 프로그래밍하지 않아도 세 쌍의 차동 신호가 나오고 보드에 차동 드라이버 칩을 둘 필요가 없습니다. 오른쪽은 조향과 승강에 다는 KTH7801 보드로, SOP-8 칩 하나와 레귤레이터만 있고 SPI 네 선과 전원, 접지만 커넥터로 나갑니다. KTH7801의 SPI는 클럭이 쉴 때 High인 모드 3이고, 한 번에 16비트를 주고받는데 이 품번은 그중 12비트가 각도, 4비트가 CRC입니다. 칩 선택 선은 2.2킬로옴으로 풀업해 MCU가 켜지기 전에는 선택되지 않게 했습니다. 두 보드 모두 뒷면에 커넥터와 레귤레이터가 있어, 케이블로 받은 5볼트를 3.3볼트로 낮춰 칩에 줍니다. (전환)""",
    [(f'{TEAM} mt6701_1–3', 'MT_DS V1.0.0: U1 MT6701QT-ACD(VQFN16) — 6 A · 7 B · 8 Z, 11 U → A\\, 12 V → B\\, 9 W → Z\\, 14 MODE → GND, 13 VDD 3V3, C3 1 µF · C1 100 nF; U2 TLV70233DBVR VCC → 3V3, C2 · C4 1 µF; CN1 HX JN1.27-2x4P 1 VCC · 2 GND · 3 A · 4 A\\ · 5 B · 6 B\\ · 7 Z · 8 Z\\'),
     (f'{TEAM} kth7801_1–3', 'KTH_Enc V1.1.2: U2 KTH7801-X-C-SOP8 — 1 TEST NC, 2 MOSI, 3 CS(R4 2.2 kΩ → 3V3), 4 MISO, 5 GND, 6 PWM NC, 7 SCLK, 8 VDD(C1 100 nF · C2 1 µF); U1 TLV70233DBVR; CN1 1 VCC · 2 CS · 4 CLK · 6 MOSI · 7 GND · 8 MISO, 3 · 5 NC'),
     (DS_MT, 'QFN-16 핀 표: ABZ Differential 열 — 9 -Z, 11 -A, 12 -B (UVW_MUX = 1)'),
     (DS_MT_CN, '주문 정보: MT6701QT-ACD UVW = -A-B-Z 출고 설정'),
     (DS_KTH, 'Table 2 SOP-8 핀 (TEST 띄움), SPI CPOL = 1 · CPHA = 1 · 16비트 프레임, 5.6절 CRC 프레임 12비트 각도 + CRC-4')],
    '그림: 팀 회로도 두 장 (그린 부분만 남김)')


# ----------------------------------------------------------------- 7
add('차동 전송이 필요한 이유', '06  차동 전송이 필요한 이유', 55, f"""
<h2 class="headline">단일 종단 SPI는 3 m에서 통신 실패, LVDS는 잡음 속에서도 45 dB 이상</h2>
<div class="chart7 grow">
{snr_chart()}
{lgd(('box', GREY, '단일 종단 SPI 0.5 m'), ('box', LIGHT, 'LVDS 0.5 m'), ('x', RED, '단일 종단 SPI 3 m (통신 실패)'), ('box', BLUE, 'LVDS 3 m'))}
</div>
<div class="takeaway">그래서 바퀴 엔코더 펄스는 차동 신호로, 조향 · 승강의 SPI는 LVDS로 보냅니다 (TI 레퍼런스 디자인 시험, 1 Vpp 잡음)</div>
""",
    """차동 전송을 고른 근거입니다. TI가 SPI를 LVDS로 보내는 레퍼런스 디자인에서, 케이블에 1볼트 피크 투 피크 잡음을 주파수를 바꿔 가며 넣고 SPI로 받은 ADC 값의 신호 대 잡음비를 잰 결과입니다. 회색은 보통 SPI, 파란색은 LVDS입니다. 0.5미터에서는 잡음이 없을 때 둘 다 101데시벨이지만, 잡음 주파수가 10메가헤르츠까지 올라가면 보통 SPI는 31데시벨, LVDS는 52데시벨로 차이가 커집니다. 더 중요한 것은 3미터입니다. 빨간 X처럼 보통 SPI는 잡음이 없어도 3미터에서는 통신 자체가 되지 않았고, LVDS는 잡음이 있어도 45데시벨 이상을 유지했습니다. 차체에서 메인보드와 조향, 승강 축 사이에 케이블이 지나가고 모터 잡음도 있으므로, 바퀴 엔코더 펄스는 차동 신호로, 조향과 승강의 SPI는 LVDS로 보내기로 정했습니다. (전환)""",
    [(TIDA, 'TI TIDA-060017 (TIDUED8, 2018-07) 3.2.1.1 Noise Immunity Test · Table 4 — 1 Vpp 잡음, ADS8910B를 SPI 슬레이브로 2 kHz 사인 입력의 SNR, CAT5 케이블, SN65LVDS31/33 EVM; 단일 종단 3 m는 모든 행 Fail「Single-ended SPI application cannot support 3m cable length」'),
     ('사용자 (2026-10-14)', 'spi.png(같은 표) 참고, 「노이즈가 없다고 가정해도 3M만 가도 신호 전송이 거의 안되는 것을 확인」')],
    '그림: TI 표 4의 수치를 막대로 다시 그림 (잡음 없음 · 100 kHz · 1 MHz · 10 MHz 네 줄만)')

# ----------------------------------------------------------------- 8
add('STDS 보드와 메인보드 LVDS', '07  STDS 보드와 메인보드 LVDS', 60, f"""
<h2 class="headline">STDS 보드가 KTH7801의 SPI를 LVDS로 바꾸고, 메인보드는 두 센서를 SPI 하나로 받음</h2>
<div class="board7 tall grow">
<div class="stack">
{r3d('82_stds_top.jpg', 'STDS 보드 3D 앞면. 16핀 칩 U8, 저항 R1–R3, 5핀 칩 U2, C1, 왼쪽 박스 헤더, 오른쪽 RJ 잭', '앞면')}
{r3d('82_stds_bottom.jpg', 'STDS 보드 3D 뒷면. RJ 잭 RJ1, SOT-23-5 레귤레이터, C3, C4, C5, 실크 STDS V1.0.0', '뒷면 (RJ50 잭과 LDO)')}
</div>
{sch('82_stds_sch.png', 'STDS 보드 회로도. SN65LVDS32DR U8이 CLK, MOSI, CS 차동 입력을 받고, 100 Ω 저항 R1–R3, SN65LVDS1DBVR U2가 MISO를 차동으로, TLV70233 U1, CN1 HX JN1.27-2x4P, RJ1 5558067-1', '회로도 (STDS V1.0.0)')}
{table(['구분', '내용'], [
    ('STDS', 'Single-ended To Differential Signal'),
    ('STDS 수신', 'SN65LVDS32 (CLK, MOSI, CS)'),
    ('STDS 송신', 'SN65LVDS1 (MISO)'),
    ('메인보드', 'SN65LVDS31 송신, 32 수신'),
    ('MISO 버퍼', 'LVDS는 Hi-Z가 안 돼 CS로 끊음'),
    ('100 Ω 종단', '0.6 m부터 전송선로라 필요')], 'comparison h7 nwall')}
</div>
<div class="takeaway">신호 상승 10 ns 기준으로 0.6 m만 넘어도 전송선로라, 수신 쪽 차동 선 끝마다 100 Ω 종단 저항을 답니다</div>
""",
    """KTH7801 바로 옆에 두는 STDS 보드입니다. STDS는 단일 종단 신호를 차동 신호로 바꾼다는 뜻의 Single-ended To Differential Signal을 줄인 이름입니다. 메인보드에서 LVDS로 오는 클럭, MOSI, 칩 선택 세 쌍을 SN65LVDS32 수신기가 받아 보통 SPI 신호로 바꿔 KTH7801에 넘기고, KTH7801이 내는 MISO는 SN65LVDS1 송신기가 다시 LVDS로 바꿔 돌려보냅니다. 메인보드 쪽은 SN65LVDS31이 센서마다 클럭, MOSI, 칩 선택을 보내고, 돌아오는 MISO 두 쌍은 SN65LVDS32가 받습니다. 보통 SPI에서는 선택되지 않은 슬레이브가 MISO를 Hi-Z로 놓아 여러 센서가 한 선을 함께 씁니다. 그런데 LVDS를 거치면 송신기와 수신기가 MISO 선을 계속 구동해서 이 Hi-Z가 메인보드까지 전달되지 않습니다. 그래서 3상태 버퍼 SN74LVC1G125의 출력 허용 핀에 칩 선택을 연결해, 선택된 센서의 MISO만 통과시키고 나머지는 Hi-Z로 만듭니다. 수신 쪽 차동 선 사이에는 100옴 종단 저항을 답니다. 선 길이가 신호 파장의 10분의 1을 넘으면 전송선로로 보고 끝에서 반사되지 않게 임피던스를 맞춰야 하는데, 꼬임쌍 케이블에서 신호는 나노초에 약 20센티미터를 가므로 클럭 10메가헤르츠 기준으로는 2미터가 경계입니다. 하지만 KTH7801 출력의 상승 시간 10나노초를 흔히 쓰는 0.35 나누기 상승 시간으로 환산하면 약 35메가헤르츠라, 약 0.6미터부터 전송선로입니다. (전환)""",
    [(f'{TEAM} stds_1–3', 'STDS = Single-ended To Differential Signal (사용자 2026-10-14); STDS V1.0.0: U8 SN65LVDS32DR (1A/1B CLK, 2A/2B MOSI, 4A/4B CS → CLK · MOSI · CS), R1–R3 100 Ω (D–D\\ 사이), U2 SN65LVDS1DBVR (MISO → MISO_D · MISO_D\\), U1 TLV70233DBVR, CN1 HX JN1.27-2x4P, RJ1 5558067-1'),
     (MAIN, 'U6 · U7 SN65LVDS31DR: KTH_CLK · KTH_MOSI · KTH_CS1/2 → 차동; U8 SN65LVDS32DR: KTH_MISO1/2_D → KTH_MISO1/2; U9 · U10 SN74LVC1G125DBVR: OE ← KTH_CS1 · KTH_CS2 (2.2 kΩ 풀업), Y → KTH_MISO'),
     (DS_LVDS32, 'SN65LVDS32 — 4채널 LVDS 수신, 내부 종단 없음(외부 100 Ω)'),
     (DS_LVDS1, 'SN65LVDS1 — 1채널 LVDS 송신, 100 Ω 선로용'),
     ('사용자 설명 (2026-10-14)', 'MISO 는 원래 nCS 가 High 면 Hi-Z 인데 LVDS 를 거치면 그게 안 되어 3상태 버퍼로 Hi-Z 를 만들어야 함; 회로도 확인: STDS U2 SN65LVDS1 은 출력 허용 핀이 없고, 메인보드 U8 SN65LVDS32 는 G = 3V3 · G# = AGND 로 늘 켜짐(네 채널 공용 허용 핀)'),
     (DS_LVC125, 'SN74LVC1G125 — OE Low일 때 출력, High면 고임피던스'),
     ('사용자 메모 (2026-10-14)', '전기적 길이 = 주파수 × 선 길이 / 전파 속도, 0.1(λ/10) 초과 시 전송선로; 꼬임쌍 약 20 cm/ns; 10 MHz · 2 m → 0.1'),
     ('계산', 'KTH7801 TR 10 ns(Table 9) → 0.35 / tr ≈ 35 MHz → λ/10 ≈ 0.57 m (경험식)')],
    '그림: 팀 3D 렌더 두 장 (검은 여백만 잘라 냄)과 회로도')


# ----------------------------------------------------------------- 9
delay_rows = [(n, f'{d:g} ns') for n, d in DELAYS]
delay_rows.insert(2, ('케이블 (가는 길)', '길이 × 5 ns/m'))
delay_rows.insert(5, ('케이블 (오는 길)', '길이 × 5 ns/m'))
add('MISO 왕복 지연과 최대 SCLK', '08  클럭 · MISO 왕복 지연', 60, f"""
<h2 class="headline">MISO 왕복 지연 때문에 케이블 3 m에서 SCLK는 약 5 MHz까지</h2>
<div class="hw7 grow">
<table class="comparison h7 dly7"><tr><th>구간</th><th>최대 지연</th></tr>
{''.join(f'<tr><td>{n}</td><td>{d}</td></tr>' for n, d in delay_rows)}
<tr class="sum"><td>합계</td><td>{CHIP_NS:.1f} ns + 길이 × 10 ns/m</td></tr></table>
<div class="chart7">
<p class="cap7">SCLK 반 주기 안에 MISO가 돌아오는 최대 클럭</p>
{fmax_chart()}
</div>
</div>
<div class="takeaway">MISO는 왕복이라 케이블 길이를 정한 뒤 SCLK를 그 아래로 잡습니다 (SPI 연장 전용 칩 LTC4332도 10 m에서 2 MHz)</div>
""",
    f"""그러면 클럭은 얼마까지 올릴 수 있을까요. MOSI와 칩 선택은 클럭과 같은 방향으로 함께 가므로, 네 쌍의 선 길이를 맞춰 도착 시간 차이만 줄이면 됩니다. 문제는 MISO입니다. MCU가 클럭을 보내면 그 클럭이 케이블을 지나 센서에 닿고, 센서가 데이터를 내면 그 데이터가 다시 케이블을 지나 돌아와야 합니다. KTH7801은 모드 3이라 MCU는 클럭 반 주기 뒤에 MISO를 읽으므로, 이 왕복이 반 주기 안에 끝나야 합니다. 왼쪽 표는 이 경로의 칩마다 데이터시트 최대 지연을 더한 것으로, 칩만 {CHIP_NS:.1f}나노초이고 그중 50나노초가 KTH7801의 출력 지연입니다. 케이블은 1미터당 왕복 10나노초씩 늘어납니다. 이렇게 계산하면 케이블이 없어도 약 {f_max(0):.1f}메가헤르츠, 1미터에서 약 {f_max(1):.1f}, 3미터에서 약 {f_max(3):.1f}메가헤르츠가 한계입니다. SPI를 멀리 보내는 전용 칩인 아날로그 디바이스의 LTC4332도 10미터에서 클럭을 2메가헤르츠로 잡고 있습니다. 모두 최악값 기준이고 MCU의 입력 준비 시간은 빠져 있으므로, 실제 케이블 길이를 정한 뒤 이보다 낮게 잡고 실측으로 확인하겠습니다. (전환)""",
    [(DS_KTH, 'Table 9 TDV ≤ 50 ns (MISO 유효, 20 pF), SPI CPOL = 1 · CPHA = 1'),
     (DS_LVDS31, 'SN65LVDS31 8.8 Switching (SN65LVDSxxxx) tPHL 최대 2.5 ns'),
     (DS_LVDS32, 'SN65LVDS32 8.8 tPLH · tPHL 최대 3 ns'),
     (DS_LVDS1, 'SN65LVDS1 6.7 Driver Switching tPLH · tPHL 최대 3.1 ns'),
     (DS_LVC125, 'SN74LVC1G125 5.6 tpd 최대 3.7 ns (3.3 V ± 0.3 V, 15 pF)'),
     ('계산', f'칩 합 {CHIP_NS:.1f} ns, 케이블 20 cm/ns → 왕복 10 ns/m, f_max = 1 / (2 × (칩 합 + 왕복)) → '
             + ', '.join(f'{m} m {f_max(m):.2f} MHz' for m in LENGTHS) + ' (MCU 입력 준비 시간 제외, 최악값)'),
     (DS_LTC4332, 'Analog Devices LTC4332 SPI 연장 칩 — 「2MHz SCK Over 10m, Operation Up to 1200m」 (사용자가 보낸 기능 목록과 같음)'),
     ('사용자 메모 (2026-10-14)', 'MOSI · MISO · SCLK · nCS 길이를 맞춰 skew 최소화, MISO는 역방향이라 왕복 지연이 최대 속도를 제한')],
    '그림: 계산값을 막대로 그림')

# ----------------------------------------------------------------- 10
add('전원과 커넥터', '09  전원과 커넥터', 55, f"""
<h2 class="headline">RJ50 한 가닥에 차동 4쌍과 5 V를 실어 보내고, 센서 보드 LDO에서 3.3 V로 낮춤</h2>
<div class="hw7 grow">
<div class="stack">
{sch('83_main_rj.png', '메인보드 RJ1, RJ2 5558067-1. 1–8번에 CLK, MOSI, CS, MISO 차동 쌍, 9번 5V, 10번과 11, 12번 GND', '메인보드 RJ1 · RJ2')}
{table(['핀', '1, 2', '3, 4', '5, 6', '7, 8', '9', '10'], [('신호', 'CLK', 'MOSI', 'CS', 'MISO', '5 V', 'GND')], 'comparison h7 pins7')}
</div>
<div class="stack">
{table(['전원', '3.3 V로 직접', '5 V + LDO'], [
    ('센서 칩 최저 전압', '3.0 V', '3.0 V'),
    ('케이블 강하 여유', '0.3 V', '<b>약 1.3 V</b>')], 'comparison h7 nwall')}
{table(['커넥터', '판단'], [
    ('RJ45 (8핀)', '차동 4쌍이면 전원 자리가 없음'),
    ('범용 핀 헤더', '차동용이 아니라 임피던스를 따로 따져야 함'),
    ('<b>RJ50 (10핀)</b>', '<b>4쌍과 전원, RJ45 계열 모듈러 잭</b>')])}
</div>
</div>
<div class="takeaway">5 V로 보내면 케이블에서 1 V 넘게 떨어져도 센서에는 3.3 V가 일정하게 갑니다 (TLV70233, 300 mA에서 드롭아웃 0.375 V)</div>
""",
    """전원과 커넥터입니다. 센서 칩은 MT6701과 KTH7801 모두 최저 3.0볼트에서 동작합니다. 3.3볼트를 메인보드에서 그대로 보내면 케이블과 커넥터에서 0.3볼트만 떨어져도 최저 전압에 닿습니다. 그래서 전원은 5볼트로 보내고 각 센서 보드의 LDO 레귤레이터 TLV70233에서 3.3볼트로 낮춥니다. 이 레귤레이터는 최대 부하 300밀리암페어에서도 입력이 출력보다 0.375볼트만 높으면 되므로, 1.3볼트 가까이 떨어져도 센서에는 3.3볼트가 일정하게 갑니다. KTH7801 쪽 케이블에는 차동 네 쌍과 5볼트, 접지까지 열 가닥이 필요한데, 랜선의 RJ45는 8핀이라 전원 자리가 없고, 일반 핀 헤더는 차동 신호용이 아니어서 커넥터 구간의 임피던스를 따로 따져야 합니다. 그래서 RJ45를 10핀으로 늘린 같은 계열의 RJ50을 골랐고, 왼쪽 아래 표처럼 1번부터 8번까지 네 쌍, 9번에 5볼트, 10번에 접지를 두었습니다. (전환)""",
    [('사용자 (2026-10-14)', '「3.3V 역시 길게 가면 전압 강하가 예상되므로 5V로 보내서 3.3V LDO로 강하」, 「다른 선들은 솔직히 차동신호용으로 개발된것도 아니여서 커낵터의 임피던스를 고려해봐야하는데 … RJ45의 확장판으로 나온 RJ50」'),
     (MAIN, 'RJ1 · RJ2 5558067-1: 1/2 KTH_CLK_D · D\\, 3/4 KTH_MOSI_D · D\\, 5/6 KTH_CSx_D · D\\, 7/8 KTH_MISOx_D · D\\, 9 5V, 10 GND, 11 · 12 GND'),
     (f'{TEAM} mt6701_3 · kth7801_3 · stds_1', 'TLV70233DBVR VCC → IN · EN, OUT 3V3, C 1 µF × 2 (세 보드 같은 구성); STDS RJ1 같은 핀 배정'),
     (DS_LDO, 'TLV702 — IOUT 0–300 mA, VDO 최대 375 mV (300 mA)'),
     (DS_MT, 'MT6701 VDD 3.0–5.5 V'),
     (DS_KTH, 'KTH7801 Table 7 동작 전압 최소 3.0 V (3.3 V 판)'),
     ('계산', '3.3 − 3.0 = 0.3 V; 5 − 3.3 − 0.375 ≈ 1.3 V')],
    '그림: 팀 메인보드 회로도 1쪽에서 잘라 냄')


# ----------------------------------------------------------------- 11
add('커넥터 핀 간격 질문', '10  커넥터 핀 간격', 55, """
<h2 class="headline">KTH7801 보드 커넥터를 2.54 mm와 1.27 mm로 그려 비교 (최종 파일은 1.27 mm)</h2>
<div class="pcb7 grow">
<div class="pcbimgs">
<p class="rl">2.54 mm</p>
<figure class="shot"><img class="media" src="assets/75_enc_top.jpg" alt="KTH7801 보드 2.54 mm 판 앞면. 왼쪽에 8핀 칩 U2(KTH7801)와 고정 구멍 두 개, 가운데 C1 · C3 · R4, 오른쪽에 2열 4핀 단자"><figcaption>앞면</figcaption></figure>
<figure class="shot"><img class="media" src="assets/75_enc_bottom.jpg" alt="KTH7801 보드 2.54 mm 판 뒷면. 2열 4핀 박스 헤더가 보드보다 크게 나와 있음"><figcaption>뒷면 (박스 헤더)</figcaption></figure>
<p class="rl">1.27 mm</p>
<figure class="shot"><img class="media" src="assets/75_enc127_top.jpg" alt="KTH7801 보드 1.27 mm 판(V1.0.1) 앞면. 같은 부품 배치에 2열 4핀 단자가 촘촘해짐"><figcaption>앞면</figcaption></figure>
<figure class="shot"><img class="media" src="assets/75_enc127_layout.jpg" alt="KTH7801 보드 1.27 mm 판(V1.0.1) PCB 배치도. 2열 4핀 커넥터 CN1 에 3V3, CS, CLK, MOSI, MISO, GND 가 배정되어 있고 실크에 KTH_Enc V1.0.1"><figcaption>배치도 (CN1 핀 배정)</figcaption></figure>
</div>
<table class="comparison t7 pcbq7">
<tr><th>핀 간격</th><th>2.54 mm</th><th>1.27 mm</th></tr>
<tr><td>커넥터 크기</td><td>보드보다 큼</td><td class="blue"><b>가로와 세로 약 절반</b></td></tr>
<tr><td>납땜</td><td class="blue"><b>손납땜 쉬움</b></td><td>정밀 납땜 필요</td></tr>
<tr><td>케이블 구하기</td><td class="blue"><b>납작 케이블 흔함</b></td><td>선택지 적음</td></tr>
</table>
</div>
""",
    """여쭤보고 싶은 것이 있습니다. 엔코더 보드의 커넥터 핀 간격입니다. 위는 KTH7801 보드를 2.54밀리미터 커넥터로 그린 이전 판이고, 아래는 1.27밀리미터로 바꾼 판입니다. 2.54밀리미터 판은 뒷면 커넥터가 보드보다 크게 튀어나와 있습니다. 1.27밀리미터로 바꾸면 커넥터가 가로세로 절반 정도로 줄어 보드를 작게 만들 수 있고, 지금 최종 파일은 모두 1.27밀리미터로 그렸습니다. 다만 납땜이 까다롭고 맞는 케이블의 선택지가 적습니다. 2.54밀리미터는 크지만 손납땜이 쉽고 박스 헤더용 납작 케이블을 쉽게 구할 수 있습니다. 실차에 달 때 어느 쪽이 나은지 의견 부탁드립니다. (전환)""",
    [('팀 PCB 3D 렌더 (2026-10-14, 팀원 공유)', 'KTH7801 보드 2.54 mm 판 앞 · 뒷면, 1.27 mm 판(V1.0.1, 실크 KTH_Enc) 3D 앞면과 배치도 — 사용자 확인: 두 판 모두 KTH7801 보드'),
     (TEAM, '최종 파일 MT_DS V1.0.0 · KTH_Enc V1.1.2 · STDS V1.0.0 · 메인보드 모두 HX JN1.27-2x4P'),
     ('팀 메시지 (2026-10-14)', '「교수님에게 2.54 VS 1.27 물어보죠」'),
     ('사용자 (2026-10-14)', '2.54 vs 1.27 그림까지 넣어 질문 유지'),
     ('비교 표', '1.27 mm 는 2.54 mm 의 절반 간격 — 같은 핀 수면 커넥터 가로 · 세로가 약 절반 (기하 계산, 하우징 두께 제외)')],
    '그림: 팀 KTH7801 보드 이전 판 자료 네 장 (배경만 잘라 냄)')

# ----------------------------------------------------------------- 12
END_ROWS = [
    ('전원 · 구동', '12 V 모터 직결, 5 V · 3.3 V 분리, DRV8244 4채널', '모터 전류 실측 → 전류 제한'),
    ('엔코더', '바퀴 MT6701 증분, 조향 · 승강 KTH7801 절대', '보드 제작, 자석 정렬 브래킷'),
    ('신호 전송', '바퀴는 차동 펄스, SPI는 STDS로 LVDS', '케이블 길이 정한 뒤 SCLK 결정 → 실측'),
    ('메인보드', '모터 · 센서 쪽 회로도', 'PCB 배치 → 제작'),
    ('커넥터', '1.27 mm 2×4, RJ50 10핀', '핀 간격 결정'),
]
add('결론 및 향후 작업', '11  결론 및 향후 작업', 55, f"""
<h2 class="headline">보드 4종과 신호 · 전원 방식을 정했고, 다음은 모터 전류 실측과 보드 제작</h2>
<table class="comparison h7 concl7 grow"><tr><th>구분</th><th>결론</th><th>향후 작업</th></tr>
{''.join(f'<tr><td>{g}</td><td>{a}</td><td class="nxt">{b}</td></tr>' for g, a, b in END_ROWS)}</table>
<div class="takeaway">다음 목표는 보드를 제작해 실차에 모터 드라이버와 엔코더를 다는 것입니다</div>
""",
    """결론과 향후 작업입니다. 이번 주에는 전원과 제어 구성을 정해 모터는 12볼트를 바로 쓰고 MCU와 센서는 5볼트와 3.3볼트로 나눠 받게 했고, 모터 드라이버는 DRV8244 네 채널로 바퀴 두 개와 조향, 승강을 구동합니다. 엔코더는 바퀴에 MT6701 증분 엔코더, 조향과 승강에 KTH7801 절대 엔코더를 쓰고, 신호는 바퀴 펄스를 차동 신호로 보내고, 조향과 승강의 SPI는 STDS 보드에서 LVDS로 바꿔 보냅니다. 앞으로는 모터 전류를 실측해 드라이버의 전류 제한을 정하고, 메인보드 PCB를 배치해 중간고사 뒤에 제작하겠습니다. 엔코더 쪽 보드는 핀 간격을 정한 뒤 제작하고, 자석과 칩의 축을 맞추는 브래킷을 함께 만들겠습니다. SPI 클럭은 케이블 길이를 정한 뒤 오늘 계산한 한계보다 낮게 잡고 실제로 재 보겠습니다. 이상으로 제가 준비한 발표를 마치겠습니다. 질문 있으시면 해 주시기 바랍니다.""",
    [('week-07-1 17쪽 일정', '10/16–22 모터 전류 실측 · PCB 설계, 10/30–11/12 구동 보드 제작'),
     ('week-05/build_deck.py 6쪽', '자석과 칩의 축 어긋남 0.3 mm 이하, 간격 0.5–2 mm를 지키는 브래킷 설계'),
     ('9쪽 계산', '케이블 길이별 최대 SCLK (최악값)')],
    '출처: 이번 덱 각 장 · 팀 일정')


TITLE = '7주차 자율 지게차 개발'
TOTAL = 640


def build():
    assert len(slides) == 12, len(slides)
    assert sum(s['seconds'] for s in slides) == TOTAL, sum(s['seconds'] for s in slides)
    sections = []
    script = [f'# {TITLE} · 발표 원고', '',
              f'{len(slides)}장 · 시간 배분 합계 {TOTAL//60}분 {TOTAL%60}초. 쪽별 배정 시간은 발표 연습 후 조정한다.', '',
              '기준일: 2026-10-14. 하드웨어만 다룬다. 보드는 회로와 PCB 설계 단계이며 아직 제작 · 측정하지 않았다. '
              '칩 수치는 데이터시트 값이고, 클럭 한계와 전압 여유는 그 값으로 계산한 최악값이다. '
              '원고는 발표자 문체(합니다체)로 썼고, (전환)은 다음 쪽으로 넘기는 자리다.', '']
    elapsed = 0
    for i, s in enumerate(slides, 1):
        source_lines = '\n'.join(f'{label}: {url}' for url, label in s['sources'])
        notes = (f"권장 {s['seconds']}초\n\n{s['notes']}\n\n"
                 f"[Sources]\n{s['foot']}\n{source_lines}\n[/Sources]")
        if i == 1:
            component = (f'<x-import component-from-global-scope="UOSSlideDS.TitleSlide" '
                         f'hint-size="100%,100%" title="{escape(s["title"], quote=True)}" '
                         f'subtitle="팔레트 핸들링 경로 생성 및 제어"></x-import>'
                         f'<img class="partner-mark" src="assets/riibotics-logo.png" '
                         f'alt="Riibotics">')
        else:
            component = (f'<x-import component-from-global-scope="UOSSlideDS.ContentSlide" '
                         f'hint-size="100%,100%" title="{escape(s["title"], quote=True)}">'
                         f'<div class="slide-body">{s["body"]}</div></x-import>')
        section_class = ' class="title-section"' if i == 1 else ''
        sections.append(
            f'<section{section_class} '
            f'data-label="{escape(s["label"], quote=True)}" data-screen-label="{i:02d}" '
            f'data-duration="{s["seconds"]}" data-speaker-notes="{escape(notes, quote=True)}" '
            f'style="background:#fff">\n{component}\n</section>')
        end = elapsed + s['seconds']
        script += [f'## {i}쪽 · {s["label"]} ({elapsed//60:02d}:{elapsed%60:02d}–{end//60:02d}:{end%60:02d}, {s["seconds"]}초)',
                   '', s['notes'], '', '[Sources]', source_lines, '[/Sources]', '']
        elapsed = end
    html = f'''<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{TITLE}</title>
<link rel="icon" href="data:,">
<script src="vendor/react.production.min.js"></script><script src="vendor/react-dom.production.min.js"></script><script src="./support.js"></script></head>
<body><x-dc><helmet><meta name="viewport" content="width=device-width, initial-scale=1"><title>{TITLE}</title>
<link rel="stylesheet" href="vendor/uos-slide-template/fonts/fonts.css"><link rel="stylesheet" href="vendor/uos-slide-template/_ds_bundle.css"><link rel="stylesheet" href="vendor/uos-slide-template/styles.css"><link rel="stylesheet" href="deck.css"><script src="vendor/uos-slide-template/_ds_bundle.js"></script></helmet>
<x-import component-from-global-scope="deck-stage" from="./deck-stage.js" width="1280" height="720" hint-size="100%,100%">
''' + '\n\n'.join(sections) + '\n</x-import></x-dc></body></html>\n'
    revision = sha256((ROOT/'deck.css').read_bytes()).hexdigest()[:12]
    html = html.replace('"deck.css"', f'"deck.css?v={revision}"')
    (ROOT/'index.html').write_text(html, encoding='utf-8')
    (ROOT/'SCRIPT.md').write_text('\n'.join(script), encoding='utf-8')
    (ROOT/'slide-metadata.json').write_text(
        json.dumps([{k: v for k, v in s.items() if k != 'body'} for s in slides],
                   ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Built {len(slides)} slides; timing {elapsed}s; '
          f'Korean script {sum(len(s["notes"]) for s in slides)} characters.')


if __name__ == '__main__':
    build()
