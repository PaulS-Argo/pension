import streamlit as st
from src.data.pension_calc import PensionCalc

# Default values
DEFAULT_CURRENT_AGE = 30
DEFAULT_RETIRE_AGE = 67

st.title('Pension Pot Calculator')


class PensionUserInterface:
    def __init__(self):
        self.default_current_age = DEFAULT_CURRENT_AGE
        self.default_retire_age = DEFAULT_RETIRE_AGE

    def submit(self, current_age, retirement_age, withdrawal_rate, calculator):
        if current_age >= retirement_age:
            st.warning("Retirement age must be greater than current age.")
            self.current_age = self.default_current_age
            self.retirement_age = self.default_retire_age

        if withdrawal_rate < 0.03:
            st.info("You're planning a very cautious withdrawal rate (<3%). "
                    "Good for longevity, but may require a larger pension pot.")

        if withdrawal_rate > 0.05:
            st.warning("You're planning a high withdrawal rate (>5%). "
                       "This may deplete your pot early unless returns are strong or you plan a shorter retirement.")
        return calculator.run()

    def user_interface(self):
        col1, col2 = st.columns([2, 2])
        with col1:
            current_age = st.number_input(
                label="Current Age", step=1, min_value=18, max_value=100, value=int(DEFAULT_CURRENT_AGE), key="age")

            retirement_age = st.number_input(
                label="Retirement Age", step=1, min_value=50, max_value=100, value=int(DEFAULT_RETIRE_AGE), key="planned_retirement_age")

            p_monthly_contribution = st.number_input(
                label="Personal Monthly Contributions", value=0, min_value=0, key="personal_monthly", step=50)
            e_monthly_contribution = st.number_input(
                label="Employer Monthly Contributions", value=0, min_value=0, key="employer_monthly", step=50)
            current_pot = st.slider(label="Current Pot", min_value=0, max_value=1000000, value=0, step=500, key="current",
                                    label_visibility="visible")
            desired_income = st.slider(label="Desired Annual Income", min_value=11500, max_value=100000, value=20000, step=500, key="desired_income",
                                       label_visibility="visible", help="This is your desired monthly income from your pension")
        with col2:
            life_expectancy = st.slider(
                "Expected age at end of retirement",
                min_value=70,
                max_value=110,
                value=100,
                step=1,
                help="How long you want your pension to last. "
                "If you retire at 60 and set 100, the calculator plans for 40 years.",

            )
            years_in_retirement = life_expectancy - retirement_age

            state_pension = st.slider(
                label="State pension", key="state_pension", min_value=0, max_value=20000, value=11500, step=50, help=(
                    "The full new UK State Pension is about £11,500 per year in today's money "
                    "(2024/25 rate). You’ll normally get this from age 66–67 if you have "
                    "35 qualifying years of National Insurance contributions. "
                    "If you have fewer qualifying years or retire abroad, it may be lower. "
                    "Use your State Pension forecast at https://www.gov.uk/check-state-pension "
                    "for a personalised estimate."
                ))
            withdrawal_rate = (
                st.slider(
                    "Planned withdrawal rate (% of pot per year)",
                    min_value=2.0,
                    max_value=6.0,
                    value=4.0,
                    step=0.25,
                    key="withdrawal_rate",
                    help=(
                        "This controls how much income your pot can safely support.\n"
                        "Example: at 4%, every £100,000 of pension pot gives you £4,000/year.\n"
                        "We use this rate together with your desired income and State Pension "
                        "to calculate the pot you need."
                    ),
                )
                / 100
            )
            real_return = (st.slider(
                "Expected real annual return (after inflation) %",
                min_value=0.0,
                max_value=6.0,
                value=3.5,
                step=0.25,
                key="real_return",
                help=(
                    "Typical planning range: 2–4% for a diversified portfolio. "
                    "Higher = more optimistic/stock-heavy; lower = conservative."
                ),
            ))/100

        calculator = PensionCalc(current_age,
                                 retirement_age,
                                 current_pot,
                                 p_monthly_contribution,
                                 e_monthly_contribution,
                                 real_return,
                                 desired_income,
                                 state_pension,
                                 withdrawal_rate,
                                 years_in_retirement)

        output = self.submit(current_age, retirement_age,
                             withdrawal_rate, calculator)

        st.markdown(output)


if __name__ == "__main__":
    calc = PensionUserInterface()
    calc.user_interface()
