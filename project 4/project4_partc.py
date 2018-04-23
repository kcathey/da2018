import pandas as pd
import statsmodels.formula.api as sm
import statsmodels.api as sma

def forward_selected(data, response, remaining, prev=[]):
    """
        based upon algorithm found at: https://planspace.org/20150423-forward_selection_with_statsmodels/
    """
    selected = []
    prv = []
    current_score, best_new_score = 0.05, 0.05
    starting_formula = "{response} ~ {prev}{selected}"

    for i in range(0,len(prev)):
        prv.append("*".join(prev[i]))
    if len(prv) > 0:
        previous = "+".join(prv)
    else:
        previous = '1'

    while remaining and current_score == best_new_score:
        current_score = 0.05
        scores_with_candidates = []
        sel = starting_formula.format(response=response, selected='*'.join(selected), prev=previous)
        sel_model = sm.ols(sel, data).fit()
        print("testing base: {}".format(sel))
        if previous == "1" or previous == "":
            previous = ""
        else:
            if previous[:1] != "+":
                previous = previous+"+"
        for candidate in remaining:
            formula = starting_formula.format(response=response, selected='*'.join(selected + [candidate]), prev=previous)
            model = sm.ols(formula, data).fit()
            print("testing addition: {}".format(formula))
            prf = sma.stats.anova_lm(sel_model,model)['Pr(>F)'].loc[1]
            scores_with_candidates.append((prf, candidate))
        scores_with_candidates.sort()
        best_new_score, best_candidate = scores_with_candidates.pop(0)
        if best_new_score < current_score:
            remaining.remove(best_candidate)
            selected.append(best_candidate)
            current_score = best_new_score
    if previous[:1] != "+" and len(selected) == 0:
        previous = previous[:-1]
    formula = starting_formula.format(response=response, selected='*'.join(selected), prev=previous)
    model = sm.ols(formula, data).fit()
    return model, formula, selected


d = pd.read_csv("DA_Clean NCSA Reserves_4.14.18-FINAL.csv")
d['ReleaseMonth'] = d['ReleaseMonth'].astype('str')
d['ReleaseYear'] = d['ReleaseYear'].astype('str')

result, f, selected = forward_selected(d,'ReservesLevel',['Region','Channel','Edition','Platform','ReleaseYear','ReleaseMonth','RelativeWeek','GameType'])

print(f)
print(selected)
print(result.summary())