import re, os
templates = ['dashboard', 'loan_request', 'reverse_auction', 'loan_repayment', 'crowdfunding', 'gig_board', 'gig_score', 'meal_drops', 'trust_profile']
for t in templates:
    path = os.path.join('templates', t + '.html')
    with open(path, encoding='utf-8', errors='ignore') as f:
        content = f.read()
    has_user_var = '{{ user.' in content
    has_side_user = 'side-user' in content
    # check which nav items appear
    nav_items = re.findall(r'nav-item[^>]*>(.*?)</a>', content, re.DOTALL)
    nav_text = [re.sub(r'<[^>]+>', '', n).strip() for n in nav_items]
    print(f"{t}:")
    print(f"  has user sidebar: {has_side_user}, uses user var: {has_user_var}")
    print(f"  nav items: {nav_text}")
    print()
