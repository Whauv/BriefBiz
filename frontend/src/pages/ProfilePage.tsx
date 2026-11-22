import { useState } from "react";

import { FollowBox } from "../components/FollowBox";
import { Panel } from "../components/Panel";
import { PreferenceGroup } from "../components/PreferenceGroup";
import { ProfileAuthPanel } from "../components/ProfileAuthPanel";
import { useFollows } from "../hooks/useFollows";
import { useNotificationData } from "../hooks/useBriefBizData";
import { usePreferencesSync } from "../hooks/usePreferencesSync";

const sectors = ["FinTech", "SaaS", "HealthTech", "DeepTech", "Consumer", "Climate", "Emerging Markets"];
const regions = ["US", "Europe", "India", "Southeast Asia", "Africa", "LatAm", "Global"];

export function ProfilePage() {
  useNotificationData();
  const { preferences, togglePreference } = usePreferencesSync();
  const { companies, investors, addCompany, addInvestor } = useFollows();
  const [companyInput, setCompanyInput] = useState("");
  const [investorInput, setInvestorInput] = useState("");

  return (
    <div className="space-y-6">
      <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <ProfileAuthPanel />

        <Panel className="p-6">
          <PreferenceGroup
            title="Sectors"
            options={sectors}
            selected={preferences.sectors}
            onToggle={(option) => togglePreference("sectors", option)}
          />
          <PreferenceGroup
            title="Regions"
            options={regions}
            selected={preferences.regions}
            onToggle={(option) => togglePreference("regions", option)}
          />
        </Panel>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <FollowBox
          title="Follow companies"
          value={companyInput}
          onChange={setCompanyInput}
          items={companies}
          placeholder="Add a company"
          onSubmit={() => {
            addCompany(companyInput);
            setCompanyInput("");
          }}
        />
        <FollowBox
          title="Follow investors"
          value={investorInput}
          onChange={setInvestorInput}
          items={investors}
          placeholder="Add an investor"
          onSubmit={() => {
            addInvestor(investorInput);
            setInvestorInput("");
          }}
        />
      </section>
    </div>
  );
}
