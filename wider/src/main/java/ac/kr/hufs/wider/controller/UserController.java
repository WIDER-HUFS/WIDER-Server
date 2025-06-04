package ac.kr.hufs.wider.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import ac.kr.hufs.wider.model.DTO.ChangePasswordDTO;
import ac.kr.hufs.wider.model.DTO.SignInDTO;
import ac.kr.hufs.wider.model.DTO.SignUpDTO;
import ac.kr.hufs.wider.model.Entity.Users;
import ac.kr.hufs.wider.model.Service.UserService;
import ac.kr.hufs.wider.service.JwtService;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    @Autowired
    private UserService userService;
    
    @Autowired
    private JwtService jwtService;

    @PostMapping("/signup")
    @CrossOrigin(origins = "*")
    public Users signup(@RequestBody SignUpDTO signUpDTO) {
        return userService.createUser(signUpDTO);
    }

    @PostMapping("/signin")
    @CrossOrigin(origins = "*")
    public ResponseEntity<?> signin(@RequestBody SignInDTO signInDTO) {
        Users user = userService.signin(signInDTO.getUserId(), signInDTO.getPassword())
                .orElseThrow(() -> new IllegalArgumentException("아이디 또는 비밀번호가 일치하지 않습니다."));
        
        String token = jwtService.generateToken(user.getUserId());
        
        Map<String, Object> response = new HashMap<>();
        response.put("user", user);
        response.put("token", token);
        
        return ResponseEntity.ok(response); // HTTP 200 + 응답 본문
    }


    @GetMapping("/{userId}/info")
    @CrossOrigin(origins = "*")
    public Users getUserInfo(@PathVariable String userId) {
        return userService.getUserById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found with id: " + userId));
    }


    @PostMapping("/deleteUser")
    @CrossOrigin(origins = "*")
    public String deleteUser(@RequestBody SignInDTO signInDTO) {
        userService.deleteUser(signInDTO.getUserId());
        return "삭제 완료";
    }

    @PostMapping("/logout")
    @CrossOrigin(origins = "*")
    public ResponseEntity<?> logout(@RequestHeader("Authorization") String token) {
        // @RequestHeader("Authorization") String token : 헤더에서 토큰을 가져옴 (Bearer 토큰 형식)
        // 클라이언트에서 토큰을 삭제하는 코드 별도로 필요
        // 서버에서는 별도의 처리 X
        return ResponseEntity.ok().body("로그아웃 되었습니다.");
    }

   @PostMapping("/changePassword")
public String changePassword(
        @RequestHeader("Authorization") String authHeader, 
        @RequestBody ChangePasswordDTO changePasswordDTO) {

    // 1) 헤더가 "Bearer "로 시작하는지 확인
    if (authHeader == null || !authHeader.startsWith("Bearer ")) {
        throw new IllegalArgumentException("Authorization 헤더 형식이 잘못되었습니다. 'Bearer {토큰}' 형태인지 확인하세요.");
    }

    // 2) "Bearer " 접두어(7글자) 제거 → 실제 JWT만 남김
    String token = authHeader.substring(7);

    // 3) Service에 순수 토큰만 넘겨서 검증하도록
    userService.changePassword(
        token, 
        changePasswordDTO.getCurrentPassword(), 
        changePasswordDTO.getNewPassword1(), 
        changePasswordDTO.getNewPassword2()
    );

    return "비밀번호 변경 완료";
}

}
