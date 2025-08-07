package top.fish1000.pymcfabric;

import net.minecraft.server.MinecraftServer;
import top.fish1000.pymcfabric.executor.NamedAdvancedExecutor;

public interface Py4jEntryPoint {
    public Utils getUtils();

    public NamedAdvancedExecutor<MinecraftServer> getExecutor();
}
