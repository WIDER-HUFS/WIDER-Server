package ac.kr.hufs.wider.model.Service;

import java.util.List;
import java.util.Optional;

import ac.kr.hufs.wider.model.DTO.SignUpDTO;
import ac.kr.hufs.wider.model.Entity.Users;

public interface UserService {
    // 사용자 생성
    Users createUser(SignUpDTO dto);
    
    // 사용자 로그인
    Optional<Users> signin(String userId, String password);

    // 사용자 조회
    Optional<Users> getUserById(String userId);
    
    // 모든 사용자 조회
    List<Users> getAllUsers();
    
    // 사용자 정보 업데이트
    Users updateUser(SignUpDTO dto);

    // 사용자 비밀번호 변경
    void changePassword(String token, String currentPassword, String newPassword1, String newPassword2);
    
    // 사용자 삭제
    void deleteUser(String userId);
    
    // 사용자 존재 여부 확인
    boolean existsByUserId(String userId);
} 