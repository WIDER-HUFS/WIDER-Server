package ac.kr.hufs.wider.model.DAO.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import ac.kr.hufs.wider.model.DAO.LevelProgressDao;
import ac.kr.hufs.wider.model.DTO.LevelProgressResponseDTO;

@Repository
public class LevelProgressDaoImpl implements LevelProgressDao {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Override
    public List<LevelProgressResponseDTO> getLevelProgressByDate(String userId) {
        String sql = """
            SELECT 
                s.session_id,
                s.started_at,
                MAX(q.bloom_level) as max_bloom_level
            FROM session_logs s
            LEFT JOIN questions q ON s.session_id = q.session_id
            WHERE s.user_id = ?
            GROUP BY s.session_id, s.started_at
            ORDER BY s.started_at DESC
        """;

        return jdbcTemplate.query(sql, (rs, rowNum) ->
            LevelProgressResponseDTO.builder()
                .sessionId(rs.getString("session_id"))
                .startedAt(rs.getTimestamp("started_at").toLocalDateTime())
                .maxBloomLevel(rs.getInt("max_bloom_level"))
                .build(),
            userId
        );
    }
} 