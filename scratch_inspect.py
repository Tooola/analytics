
content = open('project/dashboard/components/bi_report.py', encoding='utf-8').read()
lines = content.splitlines(keepends=True)

# Lines are 1-indexed; we want to replace lines 559-563 (0-indexed: 558-562)
old_block = "".join(lines[558:563])
print("OLD BLOCK repr:", repr(old_block))

new_block = (
    "        _rhtml = (\n"
    "            \"<div style='padding-top:4px;'>\"\n"
    "            \"<span style='font-size:0.8rem;color:#64748B;font-weight:600;'>NIVEAU DE RISQUE</span><br/>\"\n"
    "            f\"<span style='font-size:1.1rem;font-weight:700;color:{risk_color};'>{risk_icon} {risk_raw}</span>\"\n"
    "            \"</div>\"\n"
    "        )\n"
    "        st.markdown(_rhtml, unsafe_allow_html=True)\n"
)

new_lines = lines[:558] + [new_block] + lines[563:]
new_content = "".join(new_lines)
open('project/dashboard/components/bi_report.py', 'w', encoding='utf-8').write(new_content)
print("DONE")
