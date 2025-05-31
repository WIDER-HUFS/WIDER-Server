package ac.kr.hufs.wider.model.DTO;

import java.time.LocalDate;

public class MonthlyBloomLevelCountDTO {
    private LocalDate month;     // completedMonth
    private Integer level;       // finalBloomLevel
    private Long count;          // 건수

    public MonthlyBloomLevelCountDTO(LocalDate month, Integer level, Long count) {
        this.month = month;
        this.level = level;
        this.count = count;
    }

    public LocalDate getMonth()  { return month; }
    public Integer getLevel()    { return level; }
    public Long getCount()       { return count; }
}
