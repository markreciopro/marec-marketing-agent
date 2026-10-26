import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "leads.db")

def get_staged_drafts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, l.id, c.id, c.first_name, c.last_name, c.email, comp.name, a.subject, a.content
        FROM outreach_activities a
        JOIN leads_v2 l ON a.lead_id = l.id
        JOIN contacts c ON l.contact_id = c.id
        JOIN companies comp ON c.company_id = comp.id
        WHERE a.status = 'draft'
    """)
    drafts = cursor.fetchall()
    conn.close()
    return drafts

def interactive_review():
    while True:
        drafts = get_staged_drafts()
        if not drafts:
            print("\n✓ No pending drafts found awaiting review.")
            break

        print(f"\n=================== PENDING DRAFTS ({len(drafts)}) ===================")
        for idx, draft in enumerate(drafts, 1):
            activity_id, lead_id, contact_id, first, last, email, company, subject, content = draft
            print(f"[{idx}] {company} | Recipient: {first} {last} <{email}>")

        choice = input("\nEnter draft number to review (or 'q' to quit): ").strip()
        if choice.lower() == 'q':
            break
        
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(drafts):
            print("Invalid selection.")
            continue

        selected = drafts[int(choice) - 1]
        act_id, lead_id, contact_id, first, last, email, company, subject, content = selected

        print("\n" + "="*65)
        print(f"REVIEWING DRAFT FOR: {company}")
        print(f"Recipient: {first} {last} <{email}>")
        print(f"Subject  : {subject}")
        print("-" * 65)
        print(content)
        print("="*65)

        action = input("\nAction: [A]pprove & Mark Ready | [E]dit Recipient/Body | [D]elete | [B]ack: ").strip().lower()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if action == 'a':
            cursor.execute("UPDATE outreach_activities SET status = 'approved' WHERE id = ?", (act_id,))
            cursor.execute("UPDATE leads_v2 SET stage = 'Qualified' WHERE id = ?", (lead_id,))
            conn.commit()
            print(f"✓ Draft #{act_id} approved! Lead stage moved to 'Qualified'.")
        elif action == 'e':
            new_first = input(f"Enter First Name [{first}]: ").strip() or first
            new_last = input(f"Enter Last Name [{last}]: ").strip() or last
            new_email = input(f"Enter Email [{email}]: ").strip() or email
            
            print("\nEnter new message content (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            new_content = "\n".join(lines) if lines else content

            cursor.execute("UPDATE contacts SET first_name=?, last_name=?, email=? WHERE id=?", (new_first, new_last, new_email, contact_id))
            cursor.execute("UPDATE outreach_activities SET content=? WHERE id=?", (new_content, act_id))
            conn.commit()
            print("✓ Draft updated successfully!")
        elif action == 'd':
            cursor.execute("DELETE FROM outreach_activities WHERE id = ?", (act_id,))
            conn.commit()
            print("✓ Draft deleted.")

        conn.close()

if __name__ == "__main__":
    interactive_review()