with open('gold_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos_ld = text.find('<script type="application/ld+json">')
pos_end = text.find('</script>', pos_ld)
pos_switch = text.find('function switchPortalView')

print("pos_ld:", pos_ld)
print("pos_end:", pos_end)
print("pos_switch:", pos_switch)
print("Trapped inside JSON-LD:", pos_ld < pos_switch < pos_end)
