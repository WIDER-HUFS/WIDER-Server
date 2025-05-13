package ac.kr.hufs.wider.model.DAO.Impl;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import ac.kr.hufs.wider.model.DAO.UserDao;
import ac.kr.hufs.wider.model.Entity.Users;
import ac.kr.hufs.wider.model.Repository.UserRepository;

@Service
public class UserDaoImpl implements UserDao {
    @Autowired
    private UserRepository userRepository;

    @Override
    public Users save(Users user) {
        return userRepository.save(user);
    }

    @Override
    public Optional<Users> findById(String userId) {
        return userRepository.findById(userId);
    }

    @Override
    public List<Users> findAll() {
        return userRepository.findAll();
    }

    @Override
    public boolean existsById(String userId) {
        return userRepository.existsById(userId);
    }

    @Override
    public void deleteById(String userId) {
        userRepository.deleteById(userId);
    }
}
