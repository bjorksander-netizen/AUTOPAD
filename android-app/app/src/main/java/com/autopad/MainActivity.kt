package com.autopad

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.autopad.connection.ConnectionManager
import com.autopad.ui.*

class MainActivity : AppCompatActivity() {

    private lateinit var connectionManager: ConnectionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        connectionManager = ViewModelProvider(this)[ConnectionManager::class.java]

        if (savedInstanceState == null) {
            loadFragment(HomeFragment())
        }

        val bottomNav = findViewById<com.google.android.material.bottomnavigation.BottomNavigationView>(R.id.bottom_nav)
        bottomNav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> { loadFragment(HomeFragment()); true }
                R.id.nav_trackpad -> { loadFragment(TrackpadFragment()); true }
                R.id.nav_keyboard -> { loadFragment(KeyboardFragment()); true }
                R.id.nav_clipboard -> { loadFragment(ClipboardFragment()); true }
                else -> false
            }
        }
    }

    private fun loadFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, fragment)
            .commit()
    }

    fun navigateTo(itemId: Int) {
        val bottomNav = findViewById<com.google.android.material.bottomnavigation.BottomNavigationView>(R.id.bottom_nav)
        bottomNav.selectedItemId = itemId
    }
}
