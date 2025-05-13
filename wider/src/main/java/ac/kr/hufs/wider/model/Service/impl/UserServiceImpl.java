package ac.kr.hufs.wider.model.Service.impl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import ac.kr.hufs.wider.model.DAO.UserDao;
import ac.kr.hufs.wider.model.DTO.SignUpDTO;
import ac.kr.hufs.wider.model.Entity.Users;
import ac.kr.hufs.wider.model.Service.UserService;
import ac.kr.hufs.wider.service.JwtService;

@Service
@Transactional
public class UserServiceImpl implements UserService {

    private final UserDao userDao;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    @Autowired
    public UserServiceImpl(UserDao userDao, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userDao = userDao;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    @Override
    public Users createUser(SignUpDTO dto) {
        if (dto.getPassword() == null || dto.getPassword().trim().isEmpty()) {
            throw new IllegalArgumentException("Password cannot be null or empty");
        }
        
        // 비밀번호 암호화
        String encodedPassword = passwordEncoder.encode(dto.getPassword());
        
        // DTO를 Users 엔티티로 변환
        Users user = new Users();
        user.setUserId(dto.getUserId());
        user.setPassword(encodedPassword);
        user.setBirthDate(dto.getBirthDate());
        user.setGender(Users.Gender.valueOf(dto.getGender().toUpperCase()));
        
        return userDao.save(user);
    }

    @Override
    public Optional<Users> getUserById(String userId) {
        return userDao.findById(userId);
    }

    @Override
    public List<Users> getAllUsers() {
        return userDao.findAll();
    }

    @Override
    public Users updateUser(SignUpDTO dto) {
        if (!userDao.existsById(dto.getUserId())) {
            throw new IllegalArgumentException("User not found with id: " + dto.getUserId());
        }
        
        Users user = userDao.findById(dto.getUserId()).orElseThrow(() -> new IllegalArgumentException("User not found with id: " + dto.getUserId()));
        user.setPassword(passwordEncoder.encode(dto.getPassword()));
        user.setBirthDate(dto.getBirthDate());
        user.setGender(Users.Gender.valueOf(dto.getGender().toUpperCase()));
        return userDao.save(user);
    }

    @Override
    public void changePassword(String token, String currentPassword, String newPassword1, String newPassword2) {
        String userId = jwtService.extractUsername(token);
        Optional<Users> user = userDao.findById(userId);
        if (!passwordEncoder.matches(currentPassword, user.get().getPassword())) {
            throw new IllegalArgumentException("현재 비밀번호가 일치하지 않습니다.");
        }
        if (!newPassword1.equals(newPassword2)) {
            throw new IllegalArgumentException("새 비밀번호가 일치하지 않습니다.");
        }
        user.get().setPassword(passwordEncoder.encode(newPassword1));
        userDao.save(user.get());
    }

    @Override
    public void deleteUser(String userId) {
        userDao.deleteById(userId);
    }

    @Override
    public boolean existsByUserId(String userId) {
        return userDao.existsById(userId);
    }

    @Override
    public Optional<Users> signin(String userId, String password) {
        Optional<Users> user = userDao.findById(userId);
        if (!user.isPresent() || !passwordEncoder.matches(password, user.get().getPassword())) {
            throw new IllegalArgumentException("아이디 또는 비밀번호가 일치하지 않습니다.");
        }
        return user;
    }
    
} 