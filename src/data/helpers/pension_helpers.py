import pandas as pd
import datetime
import math


class PensionHelpers():

    def monthly_rate_from_annual(real_annual_return: float) -> float:
        """Convert an annual real return to an equivalent monthly rate."""
        return (1.0 + real_annual_return) ** (1.0 / 12.0) - 1.0

    def pmt(rate: float, nper: int, pv: float, fv: float = 0.0, when: int = 1) -> float:
        """
        Excel-like PMT.

        rate: period rate
        nper: number of periods
        pv: present value (use negative if it's a deposit/asset)
        fv: future value (target)
        when: 1 = payment at beginning, 0 = end (default 1 to be conservative)
        """
        if rate == 0:
            return -(fv + pv) / nper
        adj = (1 + rate) if when == 1 else 1.0
        return -(rate * (fv + pv * (1 + rate) ** nper)) / (adj * ((1 + rate) ** nper - 1))

    def sustainable_income(pot: float, withdrawal_rate: float, state_pension: float) -> float:
        """Estimated sustainable income in real terms given pot + state pension."""
        return pot * withdrawal_rate + state_pension

    @staticmethod
    def years_sustainable_fixed_income(pot, desired_income, state_pension, real_return):
        """
        Returns how many years the pot can sustain the desired income (real terms).

        - Income needed from pot each year = desired_income - state_pension
        - Pot grows at `real_return` (e.g. 0.035 for 3.5%) in real terms.
        - Withdrawals are inflation-adjusted, so this is all in real terms.
        """
        annual_from_pot = desired_income - state_pension

        # If state pension alone covers desired income
        if annual_from_pot <= 0:
            return math.inf

        if pot <= 0:
            return 0.0

        r = real_return

        # No growth case: straight-line depletion
        if r == 0:
            return pot / annual_from_pot

        # If growth on pot already covers withdrawals => theoretically infinite
        if pot * r >= annual_from_pot:
            return math.inf

        # Annuity depletion formula rearranged:
        # pot = withdraw * (1 - (1 + r)^-n) / r
        # => n = -ln(1 - r * pot / withdraw) / ln(1 + r)
        x = 1 - r * pot / annual_from_pot
        if x <= 0:
            # Numerical edge / already unsustainable
            return 0.0

        years = -math.log(x) / math.log(1 + r)
        return max(0.0, years)

    def build_projection(
        current_age: int,
        retire_age: int,
        current_balance: float,
        monthly_personal: float,
        monthly_employer: float,
        annual_real_return: float,
    ) -> pd.DataFrame:
        """
        Build a year-by-year projection (real terms).
        Growth approximation: apply annual growth to the average of start balance and contributions.
        """
        years = retire_age - current_age
        annual_contrib = (monthly_personal + monthly_employer) * 12.0
        rows = []
        start_balance = float(current_balance)
        this_year = datetime.datetime.now().year

        for y in range(years + 1):
            age = current_age + y
            year = this_year + y
            if y == 0:
                contrib = 0.0
                growth = 0.0
                end_balance = start_balance
            else:
                contrib = annual_contrib
                growth = (start_balance + contrib / 2.0) * annual_real_return
                end_balance = start_balance + contrib + growth

            rows.append(
                {
                    "Year #": y,
                    "Calendar Year": year,
                    "Age": age,
                    "Start Balance (£)": round(start_balance, 2),
                    "Contributions (£/yr)": round(contrib, 2),
                    "Growth (£/yr)": round(growth, 2),
                    "End Balance (£)": round(end_balance, 2),
                }
            )
            start_balance = end_balance

        return pd.DataFrame(rows)
