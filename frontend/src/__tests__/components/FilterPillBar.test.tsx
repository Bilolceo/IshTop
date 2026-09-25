import { render, screen, fireEvent } from "@testing-library/react";
import { FilterPillBar } from "@/components/jobs/FilterPillBar";

jest.mock("@/hooks/useTranslation", () => ({ useTranslation: () => ({ locale: "uz", t: (k: string) => k }) }));

const base = {
  locations: [], jobTypes: [], experienceLevels: [], salaryRange: [0, 50_000_000] as [number, number],
  companies: [], datePosted: "all", isRemote: false,
};

describe("FilterPillBar part-time", () => {
  it("offers Yarim stavka and toggles job_type=part_time", () => {
    const onChange = jest.fn();
    const { rerender } = render(<FilterPillBar filters={base} onChange={onChange} isRu={false} />);
    fireEvent.click(screen.getByRole("button", { name: /Yarim stavka/ }));
    expect(onChange).toHaveBeenLastCalledWith(expect.objectContaining({ jobTypes: ["part_time"], isRemote: false }));
    rerender(<FilterPillBar filters={{ ...base, jobTypes: ["part_time"] }} onChange={onChange} isRu={false} />);
    fireEvent.click(screen.getByRole("button", { name: /Yarim stavka/ }));
    expect(onChange).toHaveBeenLastCalledWith(expect.objectContaining({ jobTypes: [] }));
  });
});
