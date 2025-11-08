#!/usr/bin/env python3
"""
Pension calculation module.
"""

from __future__ import annotations

from datetime import datetime
from src.data.helpers.pension_helpers import PensionHelpers
import math


class PensionCalc():
    def __init__(self, current_age: int = 33, retire_age: int = 67, current_pot: float = 0.0,
                 p_monthly_contribution: float = 0.0, e_monthly_contribution: float = 0.0,
                 real_return: float = 0.035, desired_income: int = 50000, state_pension: int = 11500,
                 withdrawal_rate: float = 0.04, years_in_retirement: int = 40):

        from src.data.helpers.pension_helpers import PensionHelpers
        self.helpers = PensionHelpers

        self.current_age = current_age
        self.retire_age = retire_age
        self.current_balance = current_pot
        self.monthly_personal = p_monthly_contribution
        self.monthly_employer = e_monthly_contribution
        self.annual_real_return = real_return
        self.desired_income = desired_income
        self.state_pension = state_pension
        self.withdrawal_rate = withdrawal_rate
        self.years_in_retirement = years_in_retirement

    def run(self):
        # --- Build projection ---
        proj = self.helpers.build_projection(
            current_age=self.current_age,
            retire_age=self.retire_age,
            current_balance=self.current_balance,
            monthly_personal=self.monthly_personal,
            monthly_employer=self.monthly_employer,
            annual_real_return=self.annual_real_return,
        )

        years = self.retire_age - self.current_age
        projected_pot = float(proj.iloc[-1]["End Balance (£)"])

        # Income your pot can support at the chosen withdrawal rate
        projected_income = self.helpers.sustainable_income(
            projected_pot,
            self.withdrawal_rate,   # must be 0.04, not 4
            self.state_pension,
            self.years_in_retirement
        )

        # How long your *desired* income can be sustained (ignores WR slider)
        years_supported = self.helpers.years_sustainable_fixed_income(
            projected_pot,
            self.desired_income,
            self.state_pension,
            self.annual_real_return,
        )

        return self.format_retirement_summary(
            years,
            projected_pot,
            projected_income,
            years_supported,
        )

    def format_retirement_summary(
        self,
        years,
        projected_pot,
        projected_income,
        years_supported,
    ):
        if math.isinf(years_supported):
            sustain_line = (
                f"📆 At your desired income of £{self.desired_income:,.0f}/yr, "
                "this looks **sustainable indefinitely** under your return assumptions."
            )
        elif years_supported <= 0:
            sustain_line = (
                "📆 Your pot would not sustain the desired income under current assumptions — "
                "you may need a larger pot, lower income, or different assumptions."
            )
        else:
            sustain_line = (
                f"📆 At your desired income of £{self.desired_income:,.0f}/yr, "
                f"your projected pot could last about **{years_supported:.0f} years**."
            )

        summary = f"""
---

## 🏦 Retirement Projection Summary — {datetime.now().year}

**Current age:** {self.current_age}  
**Retirement age:** {self.retire_age}  ({years} years to go)  

**Current pension balance:** £{self.current_balance:,.0f}  
**Monthly personal contribution:** £{self.monthly_personal:,.0f}  
**Monthly employer contribution:** £{self.monthly_employer:,.0f}  

**Expected real return:** {self.annual_real_return*100:.1f}% per year  
**Planned withdrawal rate:** {self.withdrawal_rate*100:.1f}%  
**Estimated State Pension:** £{self.state_pension:,.0f}/yr  

**Projected pot at age {self.retire_age}:** £{projected_pot:,.0f}  

---

### 💰 What your pot can support

At a **{self.withdrawal_rate*100:.1f}%** withdrawal rate, your projected pot
could support about:

👉 **£{projected_income:,.0f}/yr** (including State Pension)

---

### 🕒 Can you afford your target?

Your **desired income** is **£{self.desired_income:,.0f}/yr**.

{sustain_line}

---
"""
        return summary
