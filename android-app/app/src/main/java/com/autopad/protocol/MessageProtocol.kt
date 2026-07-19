package com.autopad.protocol

import org.json.JSONObject

data class AutopadMessage(
    val type: String,
    val data: Map<String, Any> = emptyMap(),
    val timestamp: Long = System.currentTimeMillis()
) {
    fun toJson(): String {
        val obj = JSONObject()
        obj.put("type", type)
        obj.put("data", JSONObject(data))
        obj.put("timestamp", timestamp)
        return obj.toString()
    }

    companion object {
        fun fromJson(json: String): AutopadMessage? {
            return try {
                val obj = JSONObject(json)
                val dataObj = obj.optJSONObject("data") ?: JSONObject()
                val data = mutableMapOf<String, Any>()
                dataObj.keys().forEach { key ->
                    dataObj.opt(key)?.let { data[key] = it }
                }
                AutopadMessage(
                    type = obj.getString("type"),
                    data = data,
                    timestamp = obj.optLong("timestamp", System.currentTimeMillis())
                )
            } catch (e: Exception) {
                null
            }
        }

        fun ping() = AutopadMessage("PING")
        fun pong() = AutopadMessage("PONG")

        fun connect(token: String) = AutopadMessage("CONNECT", mapOf("token" to token))

        fun mouseMove(deltaX: Int, deltaY: Int) = AutopadMessage("MOUSE_MOVE", mapOf("delta_x" to deltaX, "delta_y" to deltaY))
        fun mouseClick(button: String = "left") = AutopadMessage("MOUSE_CLICK", mapOf("button" to button))
        fun mouseDoubleClick(button: String = "left") = AutopadMessage("MOUSE_DOUBLE_CLICK", mapOf("button" to button))
        fun mouseScroll(delta: Int) = AutopadMessage("MOUSE_SCROLL", mapOf("delta" to delta))
        fun mouseDown(button: String = "left") = AutopadMessage("MOUSE_DOWN", mapOf("button" to button))
        fun mouseUp(button: String = "left") = AutopadMessage("MOUSE_UP", mapOf("button" to button))

        fun keyPress(key: String) = AutopadMessage("KEY_PRESS", mapOf("key" to key))
        fun keyRelease(key: String) = AutopadMessage("KEY_RELEASE", mapOf("key" to key))
        fun keyCombo(keys: List<String>) = AutopadMessage("KEY_COMBO", mapOf("keys" to keys))
        fun keyText(text: String) = AutopadMessage("KEY_TEXT", mapOf("text" to text))

        fun mediaPlayPause() = AutopadMessage("MEDIA_PLAY_PAUSE")
        fun mediaNext() = AutopadMessage("MEDIA_NEXT")
        fun mediaPrevious() = AutopadMessage("MEDIA_PREVIOUS")
        fun mediaStop() = AutopadMessage("MEDIA_STOP")
        fun volumeUp() = AutopadMessage("VOLUME_UP")
        fun volumeDown() = AutopadMessage("VOLUME_DOWN")
        fun volumeSet(level: Int) = AutopadMessage("VOLUME_SET", mapOf("level" to level))
        fun volumeMute() = AutopadMessage("VOLUME_MUTE")

        fun clipboardSync(content: String, source: String) = AutopadMessage("CLIPBOARD_SYNC", mapOf("content" to content, "source" to source))
        fun clipboardChanged(content: String, source: String) = AutopadMessage("CLIPBOARD_CHANGED", mapOf("content" to content, "source" to source))
        fun clipboardPush() = AutopadMessage("CLIPBOARD_PUSH")
        fun clipboardPull() = AutopadMessage("CLIPBOARD_PULL")
    }
}
