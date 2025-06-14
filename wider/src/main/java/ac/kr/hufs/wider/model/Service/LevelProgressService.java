package ac.kr.hufs.wider.model.Service;

import java.util.List;

import ac.kr.hufs.wider.model.DTO.LevelProgressResponseDTO;

public interface LevelProgressService {
    List<LevelProgressResponseDTO> getLevelProgressByDate(String userId);
} 