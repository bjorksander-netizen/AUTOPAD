package com.autopad.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import com.autopad.R
import com.autopad.connection.ConnectionManager
import com.autopad.protocol.AutopadMessage

class TrackpadFragment : Fragment() {

    private lateinit var connectionManager: ConnectionManager
    private var lastX = 0f
    private var lastY = 0f
    private var lastTapTime = 0L
    private var tapCount = 0

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_trackpad, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        connectionManager = ViewModelProvider(requireActivity())[ConnectionManager::class.java]

        val trackpadArea = view.findViewById<View>(R.id.trackpad_area)
        val btnLeftClick = view.findViewById<Button>(R.id.btn_left_click)
        val btnMiddleClick = view.findViewById<Button>(R.id.btn_middle_click)
        val btnRightClick = view.findViewById<Button>(R.id.btn_right_click)

        trackpadArea.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    lastX = event.x
                    lastY = event.y
                    val now = System.currentTimeMillis()
                    if (now - lastTapTime < 300) {
                        tapCount++
                        if (tapCount >= 2) {
                            connectionManager.sendMessage(AutopadMessage.mouseDoubleClick())
                            tapCount = 0
                        }
                    } else {
                        tapCount = 1
                    }
                    lastTapTime = now
                    true
                }
                MotionEvent.ACTION_MOVE -> {
                    val deltaX = (event.x - lastX).toInt()
                    val deltaY = (event.y - lastY).toInt()
                    if (connectionManager.isConnected()) {
                        connectionManager.sendMessage(AutopadMessage.mouseMove(deltaX, deltaY))
                    }
                    lastX = event.x
                    lastY = event.y
                    true
                }
                MotionEvent.ACTION_UP -> {
                    if (tapCount == 1 && System.currentTimeMillis() - lastTapTime >= 300) {
                        if (connectionManager.isConnected()) {
                            connectionManager.sendMessage(AutopadMessage.mouseClick())
                        }
                        tapCount = 0
                    }
                    true
                }
                else -> false
            }
        }

        var longPressTriggered = false
        trackpadArea.setOnLongClickListener {
            longPressTriggered = true
            if (connectionManager.isConnected()) {
                connectionManager.sendMessage(AutopadMessage.mouseDown("right"))
            }
            true
        }

        btnLeftClick.setOnClickListener {
            if (connectionManager.isConnected()) {
                connectionManager.sendMessage(AutopadMessage.mouseClick("left"))
            }
        }

        btnMiddleClick.setOnClickListener {
            if (connectionManager.isConnected()) {
                connectionManager.sendMessage(AutopadMessage.mouseClick("middle"))
            }
        }

        btnRightClick.setOnClickListener {
            if (connectionManager.isConnected()) {
                connectionManager.sendMessage(AutopadMessage.mouseClick("right"))
            }
        }
    }
}
