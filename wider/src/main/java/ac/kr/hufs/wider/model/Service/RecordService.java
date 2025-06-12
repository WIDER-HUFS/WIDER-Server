package ac.kr.hufs.wider.model.Service;

import java.util.List;

import ac.kr.hufs.wider.model.DTO.RecordResponseDTO;

public interface RecordService {
    /**
     * 사용자의 세션 기록을 조회합니다.
     * 같은 토픽에 대해 가장 최신 세션만 반환합니다.
     * 
     * @param userId 사용자 ID
     * @return 세션 기록 목록
     */
    List<RecordResponseDTO> getUserSessions(String userId);
} 