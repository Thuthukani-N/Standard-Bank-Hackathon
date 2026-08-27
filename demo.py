"""
Fraud rule-based flagging demo — pure Python standard library (tkinter only).
Enter transaction details, see which fraud-pattern rules trigger, and get an
overall risk score. Built for presentation purposes.

Run with:  python fraud_demo.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

RULE_LABELS = {
    'type_risk': 'Transaction type is TRANSFER or CASH_OUT',
    'error_balance_zero': 'Origin balance reconciles exactly (no discrepancy)',
    'origin_drained': 'Origin account fully drained (had funds, now zero)',
    'dest_zero_before': 'Destination account was empty before receiving funds',
    'dest_zero_after': 'Destination account still empty after receiving funds',
    'large_amount': 'Amount exceeds R200,000',
}


def flag_transaction(row):
    """If x, then rule fires. Overall score = how many rules fired."""
    rules = {
        'type_risk': row['type'] in ('TRANSFER', 'CASH_OUT'),
        'error_balance_zero': abs(row['newbalanceOrig'] + row['amount'] - row['oldbalanceOrg']) < 1,
        'origin_drained': (row['oldbalanceOrg'] > 0) and (row['newbalanceOrig'] == 0),
        'dest_zero_before': row['oldbalanceDest'] == 0,
        'dest_zero_after': row['newbalanceDest'] == 0,
        'large_amount': row['amount'] > 200_000,
    }
    rules['rule_count'] = sum(1 for k in RULE_LABELS if rules[k])
    return rules


def risk_level(count):
    if count == 0:
        return "Low"
    if count <= 2:
        return "Medium"
    if count <= 4:
        return "High"
    return "Critical"


class FraudDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fraud rule-based flagging — demo")
        self.geometry("480x560")

        fields = [
            ("Transaction type", "type", "combo"),
            ("Amount", "amount", "entry"),
            ("Origin balance before", "oldbalanceOrg", "entry"),
            ("Origin balance after", "newbalanceOrig", "entry"),
            ("Destination balance before", "oldbalanceDest", "entry"),
            ("Destination balance after", "newbalanceDest", "entry"),
        ]
        self.vars = {}

        form = ttk.Frame(self, padding=12)
        form.pack(fill='x')

        for i, (label, key, kind) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky='w', pady=6)
            if kind == "combo":
                var = tk.StringVar(value="TRANSFER")
                widget = ttk.Combobox(
                    form, textvariable=var,
                    values=["TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "DEBIT"],
                    state="readonly", width=20
                )
            else:
                var = tk.StringVar(value="0")
                widget = ttk.Entry(form, textvariable=var, width=22)
            widget.grid(row=i, column=1, sticky='w', padx=10, pady=6)
            self.vars[key] = var

        ttk.Button(self, text="Check transaction", command=self._check).pack(pady=10)

        self.risk_label = ttk.Label(self, text="", font=('TkDefaultFont', 14, 'bold'))
        self.risk_label.pack(pady=(4, 10))

        self.rule_text = tk.Text(self, height=10, width=52, state='disabled', wrap='word')
        self.rule_text.pack(padx=12)

    def _check(self):
        try:
            row = {
                'type': self.vars['type'].get(),
                'amount': float(self.vars['amount'].get()),
                'oldbalanceOrg': float(self.vars['oldbalanceOrg'].get()),
                'newbalanceOrig': float(self.vars['newbalanceOrig'].get()),
                'oldbalanceDest': float(self.vars['oldbalanceDest'].get()),
                'newbalanceDest': float(self.vars['newbalanceDest'].get()),
            }
        except ValueError:
            messagebox.showerror("Invalid input", "Balance and amount fields must be numbers.")
            return

        result = flag_transaction(row)
        count = result['rule_count']
        level = risk_level(count)

        self.risk_label.config(text=f"Risk level: {level}  —  {count} / 6 rules triggered")

        self.rule_text.config(state='normal')
        self.rule_text.delete('1.0', tk.END)
        for key, label in RULE_LABELS.items():
            mark = "[x]" if result[key] else "[ ]"
            self.rule_text.insert(tk.END, f"{mark} {label}\n")
        self.rule_text.config(state='disabled')


if __name__ == '__main__':
    app = FraudDemo()
    app.mainloop()
